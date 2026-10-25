"""Input validation functions for the NOAA API client."""

from typing import Any, Optional, Tuple

from noaa.exceptions import ValidationError

VALID_SORT_FIELDS = frozenset(
    [None, "id", "name", "mindate", "maxdate", "datacoverage"]
)
VALID_SORT_ORDERS = frozenset(["asc", "desc"])
VALID_UNITS = frozenset(["standard", "metric"])
VALID_WEATHER_UNITS = frozenset(["us", "si"])
VALID_ZONE_TYPES = frozenset(
    [
        "land",
        "marine",
        "forecast",
        "public",
        "coastal",
        "offshore",
        "fire",
        "county",
    ]
)


def validate_string_or_none(value: Any, name: str) -> None:
    """Validate that a value is a string or None."""
    if not isinstance(value, str) and value is not None:
        raise ValidationError(f"{name} should be a string")


def validate_non_empty_string(value: Any, name: str) -> None:
    """Validate that a value is a non-empty string."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")


def validate_string_or_sequence(value: Any, name: str) -> None:
    """Validate that a value is a string, sequence of strings, or None."""
    if value is None:
        return

    if isinstance(value, str):
        return

    if isinstance(value, (list, tuple)):
        for item in value:
            if not isinstance(item, str):
                raise ValidationError(
                    f"All values in {name} should be strings"
                )
        return

    raise ValidationError(f"{name} should be a string or sequence of strings")


def validate_limit(limit: int) -> None:
    """Validate the limit parameter."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValidationError("limit should be an integer")
    if limit < 0 or limit > 1000:
        raise ValidationError("limit must be between 0 and 1000")


def validate_offset(offset: int) -> None:
    """Validate the offset parameter."""
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise ValidationError("offset should be an integer")
    if offset < 0:
        raise ValidationError("offset must be non-negative")


def validate_sort_field(sort_field: Optional[str]) -> None:
    """Validate the sort_field parameter."""
    if sort_field is not None and not isinstance(sort_field, str):
        raise ValidationError("sort_field should be a string")
    if sort_field not in VALID_SORT_FIELDS:
        allowed = ", ".join(
            repr(f) if f is not None else "None"
            for f in sorted(
                VALID_SORT_FIELDS, key=lambda x: (x is not None, x)
            )
        )
        raise ValidationError(f"sort_field must be one of: {allowed}")


def validate_sort_order(sort_order: str) -> None:
    """Validate the sort_order parameter."""
    if not isinstance(sort_order, str):
        raise ValidationError("sort_order should be a string")
    if sort_order not in VALID_SORT_ORDERS:
        allowed = ", ".join(sorted(VALID_SORT_ORDERS))
        raise ValidationError(f"sort_order must be one of: {allowed}")


def validate_units(units: str) -> None:
    """Validate the units parameter."""
    if not isinstance(units, str):
        raise ValidationError("units should be a string")
    if units not in VALID_UNITS:
        allowed = ", ".join(sorted(VALID_UNITS))
        raise ValidationError(f"units must be one of: {allowed}")


def validate_boolean(value: Any, name: str) -> None:
    """Validate that a value is a boolean."""
    if not isinstance(value, bool):
        raise ValidationError(f"{name} should be a boolean")


def validate_coordinates(latitude: Any, longitude: Any) -> Tuple[float, float]:
    """Validate geographic coordinates.

    :param latitude: Latitude in degrees (-90 to 90)
    :param longitude: Longitude in degrees (-180 to 180)
    :return: Tuple of (latitude, longitude) as floats
    """
    if isinstance(latitude, bool) or not isinstance(latitude, (int, float)):
        raise ValidationError("latitude must be a numeric value")
    if isinstance(longitude, bool) or not isinstance(longitude, (int, float)):
        raise ValidationError("longitude must be a numeric value")

    lat_val = float(latitude)
    lon_val = float(longitude)

    if not -90.0 <= lat_val <= 90.0:
        raise ValidationError("latitude must be between -90 and 90 degrees")
    if not -180.0 <= lon_val <= 180.0:
        raise ValidationError("longitude must be between -180 and 180 degrees")

    return lat_val, lon_val


def validate_positive_int(
    value: Any, name: str, allow_zero: bool = True
) -> None:
    """Validate that a value is an integer >= 0.

    If allow_zero is False, the integer must be > 0.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer")
    if allow_zero and value < 0:
        raise ValidationError(f"{name} must be non-negative")
    if not allow_zero and value <= 0:
        raise ValidationError(f"{name} must be greater than 0")


def validate_weather_units(units: Optional[str]) -> None:
    """Validate Weather API units parameter."""
    if units is None:
        return
    if not isinstance(units, str) or units.lower() not in VALID_WEATHER_UNITS:
        allowed = ", ".join(sorted(VALID_WEATHER_UNITS))
        raise ValidationError(f"units must be one of: {allowed}")


def validate_zone_type(zone_type: Optional[str]) -> None:
    """Validate NWS zone type."""
    if zone_type is None:
        return
    if (
        not isinstance(zone_type, str)
        or zone_type.lower() not in VALID_ZONE_TYPES
    ):
        allowed = ", ".join(sorted(VALID_ZONE_TYPES))
        raise ValidationError(f"zone_type must be one of: {allowed}")
