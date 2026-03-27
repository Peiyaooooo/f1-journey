"""Check price alerts against current ticket prices and send email notifications."""

import logging
from datetime import datetime
import resend

from app.config import settings
from app.database import SessionLocal
from app.models.price_alert import PriceAlert
from app.models.ticket_listing import TicketListing
from app.models.user import User
from app.models.circuit import Circuit
from app.models.seat_section import SeatSection

logger = logging.getLogger(__name__)


def check_alerts():
    """Check all active price alerts and send emails for triggered ones."""
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set — skipping alert check")
        return

    resend.api_key = settings.resend_api_key
    db = SessionLocal()
    triggered = 0

    try:
        alerts = db.query(PriceAlert).filter(PriceAlert.is_active == True).all()
        logger.info(f"Checking {len(alerts)} active price alerts")

        for alert in alerts:
            # Find cheapest ticket matching the alert criteria
            query = db.query(TicketListing).filter(
                TicketListing.circuit_id == alert.circuit_id,
                TicketListing.is_available == True,
            )
            if alert.seat_section_id:
                query = query.filter(TicketListing.seat_section_id == alert.seat_section_id)

            cheapest = query.order_by(TicketListing.price.asc()).first()

            if cheapest and cheapest.price <= alert.target_price:
                # Alert triggered!
                user = db.get(User, alert.user_id)
                circuit = db.get(Circuit, alert.circuit_id)
                section = db.get(SeatSection, alert.seat_section_id) if alert.seat_section_id else None

                section_name = section.name if section else "Any section"
                circuit_name = circuit.name if circuit else "Unknown circuit"

                try:
                    resend.Emails.send({
                        "from": "F1 Journey <alerts@f1journey.com>",
                        "to": [user.email],
                        "subject": f"Price Alert: {section_name} at {circuit_name} is now ${cheapest.price:.0f}",
                        "text": (
                            f"Great news! A ticket matching your price alert is now available.\n\n"
                            f"Circuit: {circuit_name}\n"
                            f"Section: {section_name}\n"
                            f"Price: ${cheapest.price:.0f} {cheapest.currency}\n"
                            f"Source: {cheapest.source_site}\n"
                            f"Your target: ${alert.target_price:.0f}\n\n"
                            f"Buy now: {cheapest.source_url}\n\n"
                            f"— F1 Journey"
                        ),
                    })
                    logger.info(f"Alert email sent to {user.email} for {circuit_name}")
                except Exception as e:
                    logger.error(f"Failed to send alert email to {user.email}: {e}")

                alert.is_active = False
                alert.triggered_at = datetime.utcnow()
                triggered += 1

        db.commit()
        logger.info(f"Alert check complete: {triggered} alerts triggered out of {len(alerts)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_alerts()
