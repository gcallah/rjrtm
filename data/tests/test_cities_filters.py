import os
from pathlib import Path
import pytest

from server.app import create_app

@pytest.fixture()
def client(tmp_path, monkeypatch):
    data_file = tmp_path / "cities.json"
    monkeypatch.setenv("CITY_DATA_PATH", str(data_file))
    app = None
    try:
        app = create_app()
    except Exception:
        from server.app import app as _app
        app = _app
    app.config["TESTING"] = True
    c = app.test_client()

    # seed a few cities
    payloads = [
        {"name": "New York", "state": "NY", "country_code": "US"},
        {"name": "Newark", "state": "NJ", "country_code": "US"},
        {"name": "York", "state": "ENG", "country_code": "GB"},
        {"name": "Barcelona", "state": "CT", "country_code": "ES"},
    ]
    for p in payloads:
        assert c.post("/api/cities", json=p).status_code == 201
    return c

def test_filter_by_country_and_name(client):
    r = client.get("/api/cities?country_code=US&name=York")
    data = r.get_json()
    assert r.status_code == 200
    names = [c["name"] for c in data["items"]]
    assert names == ["New York"]

def test_pagination(client):
    r1 = client.get("/api/cities?per_page=2&page=1")
    r2 = client.get("/api/cities?per_page=2&page=2")
    d1, d2 = r1.get_json(), r2.get_json()
    assert d1["page"] == 1 and len(d1["items"]) == 2
    assert d2["page"] == 2 and len(d2["items"]) == 2
    assert d1["total"] >= 4
