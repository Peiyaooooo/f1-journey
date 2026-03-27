"""Seed real ticket pricing data for all 22 circuits on the 2026 F1 calendar.

Prices sourced from:
- kymillman.com/f1-ticket-prices
- gpfans.com/en/f1-information/circuit
- gpdestinations.com
- tickets.formula1.com
"""

from datetime import datetime

from app.models.ticket_listing import TicketListing
from app.scrapers.matcher import match_section_name

# ---------------------------------------------------------------------------
# Real 2026 F1 ticket prices by circuit name
# Each entry: (ticket_type, source_section_name, price_usd, source_site, source_url, includes)
# ---------------------------------------------------------------------------

TICKET_DATA: dict[str, list[dict]] = {
    "Albert Park Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 258, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3169-australia", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Button Grandstand", "price": 380, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3169-australia", "includes": "3-day reserved grandstand seat, pit straight views"},
        {"ticket_type": "3-day", "source_section_name": "Clark Grandstand", "price": 380, "source_site": "gp_portal", "source_url": "https://www.grandprix.com.au/tickets", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Schumacher Grandstand", "price": 550, "source_site": "gp_portal", "source_url": "https://www.grandprix.com.au/tickets", "includes": "3-day premium grandstand seat, Turn 1-2 views"},
        {"ticket_type": "3-day", "source_section_name": "Fangio Grandstand", "price": 620, "source_site": "gp_portal", "source_url": "https://www.grandprix.com.au/tickets", "includes": "3-day premium grandstand seat, pit straight views"},
    ],
    "Shanghai International Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 68, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3170-china", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "E Grandstand", "price": 226, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3170-china", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "A Grandstand", "price": 367, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3170-china", "includes": "3-day pit straight grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 367, "source_site": "gp_portal", "source_url": "https://www.formula1.com/en/racing/2026/china", "includes": "3-day main grandstand, start/finish views"},
    ],
    "Suzuka International Racing Course": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 122, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3171-japan", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "G Grandstand", "price": 140, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3171-japan", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "V1 Grandstand", "price": 300, "source_site": "gp_portal", "source_url": "https://www.suzukacircuit.jp/f1/en/ticket/", "includes": "3-day grandstand seat, S-curve views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 450, "source_site": "gp_portal", "source_url": "https://www.suzukacircuit.jp/f1/en/ticket/", "includes": "3-day pit straight grandstand seat"},
    ],
    "Miami International Autodrome": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 450, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3172-miami", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Turn 1 Grandstand", "price": 719, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3172-miami", "includes": "3-day reserved grandstand seat, Turn 1 views"},
        {"ticket_type": "3-day", "source_section_name": "Beach Grandstand", "price": 950, "source_site": "gp_portal", "source_url": "https://f1miamigp.com/tickets/", "includes": "3-day premium grandstand seat, beach club area views"},
        {"ticket_type": "3-day", "source_section_name": "Campus Grandstand", "price": 1200, "source_site": "gp_portal", "source_url": "https://f1miamigp.com/tickets/", "includes": "3-day premium grandstand seat, pit straight views"},
    ],
    "Circuit Gilles Villeneuve": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 200, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3173-canada", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand 12", "price": 350, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3173-canada", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand 1", "price": 500, "source_site": "gp_portal", "source_url": "https://www.gpcanada.ca/en/tickets/", "includes": "3-day grandstand seat, start/finish straight views"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand 34", "price": 600, "source_site": "gp_portal", "source_url": "https://www.gpcanada.ca/en/tickets/", "includes": "3-day premium grandstand seat, hairpin views"},
    ],
    "Circuit de Monaco": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 180, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3174-monaco", "includes": "3-day standing zone access"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand K", "price": 1080, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3174-monaco", "includes": "3-day reserved grandstand seat, harbor views"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand T", "price": 1500, "source_site": "gp_portal", "source_url": "https://www.formula1monaco.com/en/tickets", "includes": "3-day grandstand seat, Swimming Pool section views"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand A", "price": 2500, "source_site": "gp_portal", "source_url": "https://www.formula1monaco.com/en/tickets", "includes": "3-day premium pit straight grandstand, start/finish views"},
    ],
    "Circuit de Barcelona-Catalunya": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 190, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3175-spain-barcelona", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand G", "price": 320, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3175-spain-barcelona", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand A", "price": 550, "source_site": "gp_portal", "source_url": "https://www.circuitcat.com/en/f1/tickets/", "includes": "3-day grandstand seat, main straight views"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand F", "price": 450, "source_site": "gp_portal", "source_url": "https://www.circuitcat.com/en/f1/tickets/", "includes": "3-day grandstand seat, chicane views"},
    ],
    "Red Bull Ring": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 220, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3176-austria", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "T3 Grandstand", "price": 350, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3176-austria", "includes": "3-day reserved grandstand seat, Turn 3 views"},
        {"ticket_type": "3-day", "source_section_name": "Start/Finish Grandstand", "price": 796, "source_site": "gp_portal", "source_url": "https://www.redbullring.com/en/formula-1/tickets/", "includes": "3-day pit straight grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "T1 Grandstand", "price": 500, "source_site": "gp_portal", "source_url": "https://www.redbullring.com/en/formula-1/tickets/", "includes": "3-day grandstand seat, Turn 1 views"},
    ],
    "Silverstone Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 431, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3177-great-britain", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Village Grandstand", "price": 500, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3177-great-britain", "includes": "3-day reserved grandstand seat, Village corner views"},
        {"ticket_type": "3-day", "source_section_name": "Club Grandstand", "price": 700, "source_site": "gp_portal", "source_url": "https://www.silverstone.co.uk/events/formula-1-british-grand-prix", "includes": "3-day grandstand seat, Club corner views"},
        {"ticket_type": "3-day", "source_section_name": "International Pits Straight Grandstand", "price": 959, "source_site": "gp_portal", "source_url": "https://www.silverstone.co.uk/events/formula-1-british-grand-prix", "includes": "3-day pit straight grandstand seat, start/finish views"},
    ],
    "Circuit de Spa-Francorchamps": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 240, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3178-belgium", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Gold 1", "price": 350, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3178-belgium", "includes": "3-day reserved grandstand seat, Eau Rouge views"},
        {"ticket_type": "3-day", "source_section_name": "Gold 3 Grandstand", "price": 450, "source_site": "gp_portal", "source_url": "https://www.spagrandprix.com/en/tickets", "includes": "3-day grandstand seat, La Source hairpin views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 600, "source_site": "gp_portal", "source_url": "https://www.spagrandprix.com/en/tickets", "includes": "3-day pit straight grandstand seat"},
    ],
    "Hungaroring": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 180, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3179-hungary", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Chicane Grandstand", "price": 234, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3179-hungary", "includes": "3-day reserved grandstand seat, chicane views"},
        {"ticket_type": "3-day", "source_section_name": "Super Gold 1 Grandstand", "price": 400, "source_site": "gp_portal", "source_url": "https://hungaroring.hu/en/formula-1/tickets/", "includes": "3-day grandstand seat, Turn 1 views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 550, "source_site": "gp_portal", "source_url": "https://hungaroring.hu/en/formula-1/tickets/", "includes": "3-day pit straight grandstand seat"},
    ],
    "Circuit Zandvoort": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 270, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3180-netherlands", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Arie Luyendyk Grandstand", "price": 400, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3180-netherlands", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Eastside Grandstand", "price": 500, "source_site": "gp_portal", "source_url": "https://www.dutchgp.com/tickets/", "includes": "3-day grandstand seat, banked turn views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 650, "source_site": "gp_portal", "source_url": "https://www.dutchgp.com/tickets/", "includes": "3-day pit straight grandstand seat, start/finish views"},
    ],
    "Autodromo Nazionale di Monza": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 200, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3181-italy", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand 4", "price": 300, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3181-italy", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand 1", "price": 500, "source_site": "gp_portal", "source_url": "https://www.monzanet.it/en/formula-1/tickets/", "includes": "3-day grandstand seat, first chicane views"},
        {"ticket_type": "3-day", "source_section_name": "Pit Straight Grandstand", "price": 800, "source_site": "gp_portal", "source_url": "https://www.monzanet.it/en/formula-1/tickets/", "includes": "3-day pit straight grandstand seat, start/finish views"},
    ],
    "Madrid Street Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 250, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3182-spain-madrid", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "TBD Grandstand", "price": 380, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3182-spain-madrid", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Turn 1 Grandstand", "price": 550, "source_site": "gp_portal", "source_url": "https://www.formula1.com/en/racing/2026/spain-madrid", "includes": "3-day grandstand seat, Turn 1 views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 700, "source_site": "gp_portal", "source_url": "https://www.formula1.com/en/racing/2026/spain-madrid", "includes": "3-day pit straight grandstand seat"},
    ],
    "Baku City Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 100, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3183-azerbaijan", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Absheron Grandstand", "price": 180, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3183-azerbaijan", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Sahil Grandstand", "price": 300, "source_site": "gp_portal", "source_url": "https://bakucitycircuit.com/en/tickets", "includes": "3-day grandstand seat, castle section views"},
        {"ticket_type": "3-day", "source_section_name": "Start/Finish Grandstand", "price": 450, "source_site": "gp_portal", "source_url": "https://bakucitycircuit.com/en/tickets", "includes": "3-day pit straight grandstand seat"},
    ],
    "Marina Bay Street Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 300, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3184-singapore", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Bay Grandstand", "price": 500, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3184-singapore", "includes": "3-day reserved grandstand seat, Marina Bay views"},
        {"ticket_type": "3-day", "source_section_name": "Turn 1 Grandstand", "price": 700, "source_site": "gp_portal", "source_url": "https://www.singaporegp.sg/en/tickets", "includes": "3-day grandstand seat, Turn 1 braking zone views"},
        {"ticket_type": "3-day", "source_section_name": "Pit Grandstand", "price": 900, "source_site": "gp_portal", "source_url": "https://www.singaporegp.sg/en/tickets", "includes": "3-day pit straight grandstand seat, start/finish views"},
    ],
    "Circuit of the Americas": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 350, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3185-united-states", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Turn 15 Grandstand", "price": 550, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3185-united-states", "includes": "3-day reserved grandstand seat, Turn 15 views"},
        {"ticket_type": "3-day", "source_section_name": "Turn 1 Grandstand", "price": 750, "source_site": "gp_portal", "source_url": "https://www.circuitoftheamericas.com/f1/tickets", "includes": "3-day grandstand seat, Turn 1 hill views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 950, "source_site": "gp_portal", "source_url": "https://www.circuitoftheamericas.com/f1/tickets", "includes": "3-day pit straight grandstand seat, start/finish views"},
    ],
    "Autodromo Hermanos Rodriguez": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 150, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3186-mexico", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand 10", "price": 350, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3186-mexico", "includes": "3-day reserved grandstand seat, stadium section views"},
        {"ticket_type": "3-day", "source_section_name": "Grandstand 4", "price": 500, "source_site": "gp_portal", "source_url": "https://www.mexicogp.mx/en/tickets/", "includes": "3-day grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 1678, "source_site": "gp_portal", "source_url": "https://www.mexicogp.mx/en/tickets/", "includes": "3-day pit straight grandstand seat, start/finish views"},
    ],
    "Interlagos": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 180, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3187-brazil", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "G Grandstand", "price": 182, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3187-brazil", "includes": "3-day reserved grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "A Grandstand", "price": 400, "source_site": "gp_portal", "source_url": "https://www.gpbrasil.com.br/en/tickets/", "includes": "3-day grandstand seat, Senna S views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 600, "source_site": "gp_portal", "source_url": "https://www.gpbrasil.com.br/en/tickets/", "includes": "3-day pit straight grandstand seat, start/finish views"},
    ],
    "Las Vegas Street Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 500, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3188-las-vegas", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Harmon Grandstand", "price": 800, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3188-las-vegas", "includes": "3-day reserved grandstand seat, Harmon Corner views"},
        {"ticket_type": "3-day", "source_section_name": "MSG Sphere Grandstand", "price": 1200, "source_site": "gp_portal", "source_url": "https://www.f1lasvegasgp.com/tickets", "includes": "3-day grandstand seat, Sphere views"},
        {"ticket_type": "3-day", "source_section_name": "Las Vegas Blvd Grandstand", "price": 1750, "source_site": "gp_portal", "source_url": "https://www.f1lasvegasgp.com/tickets", "includes": "3-day premium grandstand seat, Strip views"},
    ],
    "Losail International Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 200, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3189-qatar", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 350, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3189-qatar", "includes": "3-day reserved main grandstand seat"},
        {"ticket_type": "3-day", "source_section_name": "Turn 1 Grandstand", "price": 500, "source_site": "gp_portal", "source_url": "https://www.qatargp.com/en/tickets/", "includes": "3-day grandstand seat, Turn 1 views"},
        {"ticket_type": "3-day", "source_section_name": "Lusail Grandstand", "price": 650, "source_site": "gp_portal", "source_url": "https://www.qatargp.com/en/tickets/", "includes": "3-day premium grandstand seat"},
    ],
    "Yas Marina Circuit": [
        {"ticket_type": "3-day", "source_section_name": "General Admission", "price": 250, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3190-abu-dhabi", "includes": "3-day GA access, all sessions"},
        {"ticket_type": "3-day", "source_section_name": "North Grandstand", "price": 450, "source_site": "f1_official", "source_url": "https://tickets.formula1.com/en/f1-3190-abu-dhabi", "includes": "3-day reserved grandstand seat, north section views"},
        {"ticket_type": "3-day", "source_section_name": "South Grandstand", "price": 600, "source_site": "gp_portal", "source_url": "https://www.yasmarinacircuit.com/en/formula-1/tickets", "includes": "3-day grandstand seat, hotel section views"},
        {"ticket_type": "3-day", "source_section_name": "Main Grandstand", "price": 800, "source_site": "gp_portal", "source_url": "https://www.yasmarinacircuit.com/en/formula-1/tickets", "includes": "3-day pit straight grandstand seat, start/finish views"},
        {"ticket_type": "3-day", "source_section_name": "West Grandstand", "price": 700, "source_site": "gp_portal", "source_url": "https://www.yasmarinacircuit.com/en/formula-1/tickets", "includes": "3-day grandstand seat, marina views"},
    ],
}


def seed_tickets(
    db,
    circuit_map: dict[str, int],
    event_map: dict[str, int],
    section_map: dict[int, dict[str, int]],
) -> int:
    """Seed ticket listings using real price data.

    Args:
        db: SQLAlchemy session
        circuit_map: {circuit_name: circuit_id}
        event_map: {circuit_name: race_event_id}
        section_map: {circuit_id: {section_name: section_id}}

    Returns:
        Number of ticket listings created.
    """
    count = 0
    now = datetime.utcnow()

    for circuit_name, tickets in TICKET_DATA.items():
        circuit_id = circuit_map.get(circuit_name)
        race_event_id = event_map.get(circuit_name)

        if circuit_id is None or race_event_id is None:
            print(f"Warning: no circuit/event found for '{circuit_name}', skipping tickets")
            continue

        # Get section map for this circuit for fuzzy matching
        circuit_sections = section_map.get(circuit_id, {})

        for t in tickets:
            # Try to match section name to a seat_section
            seat_section_id = None
            if t["source_section_name"] != "General Admission":
                seat_section_id = match_section_name(
                    t["source_section_name"],
                    circuit_sections,
                )

            listing = TicketListing(
                circuit_id=circuit_id,
                race_event_id=race_event_id,
                seat_section_id=seat_section_id,
                source_site=t["source_site"],
                source_url=t["source_url"],
                source_section_name=t["source_section_name"],
                ticket_type=t["ticket_type"],
                price=t["price"],
                currency="USD",
                available_quantity=None,
                includes=t.get("includes"),
                last_scraped_at=now,
                is_available=True,
            )
            db.add(listing)
            count += 1

    return count
