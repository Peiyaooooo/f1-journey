from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.circuits import router as circuits_router
from app.routers.race_events import router as race_events_router
from app.routers.sections import router as sections_router
from app.routers.tickets import router as tickets_router
from app.routers.travel import router as travel_router
from app.routers.auth import router as auth_router
from app.routers.saved_searches import router as saved_searches_router
from app.routers.price_alerts import router as price_alerts_router
from app.routers.calendar import router as calendar_router

app = FastAPI(title="F1 Journey API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(circuits_router)
app.include_router(race_events_router)
app.include_router(sections_router)
app.include_router(tickets_router)
app.include_router(travel_router)
app.include_router(auth_router)
app.include_router(saved_searches_router)
app.include_router(price_alerts_router)
app.include_router(calendar_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/admin/seed")
def seed_database(secret: str = ""):
    """One-time seed endpoint. Requires the JWT secret as auth."""
    if secret != settings.jwt_secret:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Invalid secret")
    from app.seed.seed_data import seed
    seed()
    return {"status": "seeded"}
