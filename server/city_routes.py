from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List

from flask import Blueprint, jsonify, request, abort

city_bp = Blueprint("city", __name__, url_prefix="/cities")


@dataclass
class City:
    id: int
    name: str
    state: str
    country: str
    created_at: str
    updated_at: str


# Simple in-RAM cache for city data.
# In a later step this can be swapped for a DB layer.
_CITY_STORE: Dict[int, City] = {}
_NEXT_ID: int = 1


def _next_id() -> int:
    global _NEXT_ID
    nid = _NEXT_ID
    _NEXT_ID += 1
    return nid


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


@city_bp.route("/", methods=["GET"])
def list_cities():
    """Return all cities from the in-memory cache."""
    return jsonify([asdict(c) for c in _CITY_STORE.values()])


@city_bp.route("/", methods=["POST"])
def create_city():
    """Create a new city and store it in RAM."""
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    state = body.get("state")
    country = body.get("country")

    if not name or not state or not country:
        abort(400, description="Missing required fields: name, state, country")

    cid = _next_id()
    now = _now_iso()
    city = City(
        id=cid,
        name=name,
        state=state,
        country=country,
        created_at=now,
        updated_at=now,
    )
    _CITY_STORE[cid] = city
    return jsonify(asdict(city)), 201


@city_bp.route("/<int:city_id>", methods=["GET"])
def get_city(city_id: int):
    """Fetch a single city by ID."""
    city = _CITY_STORE.get(city_id)
    if city is None:
        abort(404, description="City not found")
    return jsonify(asdict(city))


@city_bp.route("/<int:city_id>", methods=["PUT"])
def update_city(city_id: int):
    """Update an existing city (name/state/country)."""
    city = _CITY_STORE.get(city_id)
    if city is None:
        abort(404, description="City not found")

    body = request.get_json(silent=True) or {}
    name = body.get("name", city.name)
    state = body.get("state", city.state)
    country = body.get("country", city.country)

    updated = City(
        id=city.id,
        name=name,
        state=state,
        country=country,
        created_at=city.created_at,
        updated_at=_now_iso(),
    )
    _CITY_STORE[city_id] = updated
    return jsonify(asdict(updated))


@city_bp.route("/<int:city_id>", methods=["DELETE"])
def delete_city(city_id: int):
    """Delete a city by ID."""
    if city_id not in _CITY_STORE:
        abort(404, description="City not found")
    del _CITY_STORE[city_id]
    return jsonify({"message": "City deleted"}), 200
