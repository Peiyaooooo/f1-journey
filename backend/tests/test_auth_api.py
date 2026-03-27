from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


def setup_function():
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = override_get_db


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def _register(email="test@example.com", password="secret123"):
    return client.post("/api/auth/register", json={"email": email, "password": password})


def test_register():
    resp = _register()
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email():
    _register()
    resp = _register()
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_login():
    _register()
    resp = client.post("/api/auth/login", json={"email": "test@example.com", "password": "secret123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password():
    _register()
    resp = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrongpass"})
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


def test_get_me_with_token():
    reg = _register()
    token = reg.json()["access_token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["preferred_currency"] == "USD"
    assert "id" in data


def test_get_me_without_token():
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)


def test_refresh_token():
    reg = _register()
    refresh = reg.json()["refresh_token"]
    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
