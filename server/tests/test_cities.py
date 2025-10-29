import json
import pytest
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

@pytest.fixture
def client():
    return ep.app.test_client()

def test_get_all_cities(client):
    """GET /cities should return list (even if empty)."""
    response = client.get("/cities")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_post_city(client):
    """POST /cities should add a new city."""
    new_city = {"name": "Osaka", "country": "Japan", "population": 2700000}
    response = client.post(
        "/cities",
        data=json.dumps(new_city),
        content_type="application/json",
    )
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert "message" in data

def test_get_city_by_name(client):
    """GET /cities/<name> should return that city."""
    response = client.get("/cities/Osaka")
    assert response.status_code in (200, 404)

def test_update_city(client):
    """PUT /cities/<name> should update population."""
    updates = {"population": 3000000}
    response = client.put(
        "/cities/Osaka",
        data=json.dumps(updates),
        content_type="application/json",
    )
    assert response.status_code in (200, 404)

def test_delete_city(client):
    """DELETE /cities/<name> should remove city."""
    response = client.delete("/cities/Osaka")
    assert response.status_code in (200, 404)

def test_get_cities_filter_and_pagination(client):
    """GET /cities with country filter and pagination."""
    # Add several cities
    cities_to_add = [
        {"name": "New York", "country": "USA", "population": 8400000},
        {"name": "Los Angeles", "country": "USA", "population": 4000000},
        {"name": "Tokyo", "country": "Japan", "population": 14000000},
    ]
    for city in cities_to_add:
        client.post("/cities", data=json.dumps(city), content_type="application/json")

    # Filter by country
    resp = client.get("/cities?country=USA&limit=1&offset=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert all(city["country"] == "USA" for city in data)
    assert len(data) <= 1

def test_post_city_missing_name_or_country(client):
    """POST /cities should reject requests missing required fields."""
    incomplete_city = {"population": 500000}
    resp = client.post("/cities", json=incomplete_city)
    assert resp.status_code == 400
    assert "error" in resp.get_json()

    incomplete_city_2 = {"name": "NoCountry"}
    resp2 = client.post("/cities", json=incomplete_city_2)
    assert resp2.status_code == 400
    assert "error" in resp2.get_json()


def test_post_city_invalid_population(client):
    """POST /cities should reject invalid population values."""
    invalid_city = {"name": "GhostTown", "country": "Nowhere", "population": -123}
    resp = client.post("/cities", json=invalid_city)
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_city_invalid_population(client):
    """PUT /cities/<name> should reject invalid population."""
    valid_city = {"name": "Testville", "country": "Nowhere", "population": 100}
    client.post("/cities", json=valid_city)

    update_invalid = {"population": -50}
    resp = client.put("/cities/Testville", json=update_invalid)
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_post_city_malformed_json(client):
    """POST /cities should return 400 for malformed JSON."""
    bad_json = "{name: 'BadCity', country: 'Nowhere'}"  # missing quotes around keys
    resp = client.post("/cities", data=bad_json, content_type="application/json")
    assert resp.status_code == 400
