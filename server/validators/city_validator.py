from typing import Any, Dict, List, Tuple

# Minimal schema for City payloads used by create/update endpoints.
# Required: name, state_id, country_id
# Optional: population (int >= 0)

REQUIRED_FIELDS = {"name", "state_id", "country_id"}


def validate_city_payload(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a city payload.

    Returns:
        (is_valid, errors)
        - Ensures required fields present and non-empty
        - Ensures 'population' if provided is a non-negative int
    """
    errors: List[str] = []

    # Required fields check
    missing = [f for f in REQUIRED_FIELDS if f not in payload or payload[f] in (None, "")]
    if missing:
        errors.append(f"Missing required fields: {', '.join(sorted(missing))}")

    # population rules (optional)
    if "population" in payload:
        try:
            pop = int(payload["population"])
            if pop < 0:
                errors.append("population must be non-negative")
        except (TypeError, ValueError):
            errors.append("population must be an integer")

    return (len(errors) == 0), errors
