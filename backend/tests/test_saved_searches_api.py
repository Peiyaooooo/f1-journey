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


def _auth_header(email="test@example.com", password="secret123"):
    resp = _register(email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_saved_search():
    headers = _auth_header()
    resp = client.post(
        "/api/saved-searches",
        json={"search_type": "filters", "name": "My Search", "data": {"circuit": "monza"}},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Search"
    assert data["search_type"] == "filters"
    assert data["data"] == {"circuit": "monza"}
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_list_saved_searches():
    headers = _auth_header()
    client.post(
        "/api/saved-searches",
        json={"search_type": "filters", "name": "Search 1", "data": {"a": 1}},
        headers=headers,
    )
    client.post(
        "/api/saved-searches",
        json={"search_type": "trip", "name": "Search 2", "data": {"b": 2}},
        headers=headers,
    )
    resp = client.get("/api/saved-searches", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = {s["name"] for s in data}
    assert names == {"Search 1", "Search 2"}


def test_delete_saved_search():
    headers = _auth_header()
    create_resp = client.post(
        "/api/saved-searches",
        json={"search_type": "filters", "name": "To Delete", "data": {}},
        headers=headers,
    )
    search_id = create_resp.json()["id"]
    resp = client.delete(f"/api/saved-searches/{search_id}", headers=headers)
    assert resp.status_code == 204

    # Verify it's gone
    list_resp = client.get("/api/saved-searches", headers=headers)
    assert len(list_resp.json()) == 0


def test_cannot_access_without_auth():
    resp = client.get("/api/saved-searches")
    assert resp.status_code in (401, 403)

    resp = client.post(
        "/api/saved-searches",
        json={"search_type": "filters", "name": "No Auth", "data": {}},
    )
    assert resp.status_code in (401, 403)
