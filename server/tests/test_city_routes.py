import json

from flask import Flask

# Adjust this import to however your app is created:
# - if you have app = Flask(...) in server/app.py:
from server.app import app  # type: ignore[import]


def _post_json(client, url, payload):
    return client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )


def test_create_and_get_city():
    with app.test_client() as client:
        payload = {"name": "Test City", "state": "NY", "country": "USA"}
        resp = _post_json(client, "/cities/", payload)

        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Test City"
        assert "id" in data

        city_id = data["id"]
        get_resp = client.get(f"/cities/{city_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.get_json()
        assert get_data["id"] == city_id
        assert get_data["name"] == "Test City"


def test_list_cities():
    with app.test_client() as client:
        resp = client.get("/cities/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)


def test_update_city():
    with app.test_client() as client:
        # create
        payload = {"name": "Old Name", "state": "NJ", "country": "USA"}
        resp = _post_json(client, "/cities/", payload)
        city_id = resp.get_json()["id"]

        # update
        upd_payload = {"name": "New Name"}
        upd_resp = _post_json(client, f"/cities/{city_id}", upd_payload)
        # Note: if PUT is not JSON body but form, adjust above.
        if upd_resp.status_code == 405:
            # If server expects PUT, retry with PUT
            upd_resp = client.put(
                f"/cities/{city_id}",
                data=json.dumps(upd_payload),
                content_type="application/json",
            )

        assert upd_resp.status_code == 200
        upd_data = upd_resp.get_json()
        assert upd_data["name"] == "New Name"


def test_delete_city():
    with app.test_client() as client:
        payload = {"name": "Delete Me", "state": "CA", "country": "USA"}
        resp = _post_json(client, "/cities/", payload)
        city_id = resp.get_json()["id"]

        del_resp = client.delete(f"/cities/{city_id}")
        assert del_resp.status_code == 200

        # Verify it is gone
        get_resp = client.get(f"/cities/{city_id}")
        assert get_resp.status_code == 404
