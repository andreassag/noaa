"""Tests for validation functions."""

from noaa.exceptions import ValidationError
from noaa.validators import (
    validate_boolean,
    validate_limit,
    validate_offset,
    validate_sort_field,
    validate_sort_order,
    validate_string_or_none,
    validate_string_or_sequence,
    validate_units,
)

import pytest


class TestValidateStringOrNone:
    """Tests for validate_string_or_none."""

    def test_valid_string(self):
        """Should accept valid strings."""
        validate_string_or_none("test", "param")

    def test_valid_none(self):
        """Should accept None."""
        validate_string_or_none(None, "param")

    def test_invalid_int(self):
        """Should reject integers."""
        with pytest.raises(ValidationError, match="should be a string"):
            validate_string_or_none(123, "param")

    def test_invalid_list(self):
        """Should reject lists."""
        with pytest.raises(ValidationError, match="should be a string"):
            validate_string_or_none(["a", "b"], "param")


class TestValidateStringOrSequence:
    """Tests for validate_string_or_sequence."""

    def test_valid_string(self):
        """Should accept valid strings."""
        validate_string_or_sequence("test", "param")

    def test_valid_none(self):
        """Should accept None."""
        validate_string_or_sequence(None, "param")

    def test_valid_list(self):
        """Should accept list of strings."""
        validate_string_or_sequence(["a", "b", "c"], "param")

    def test_valid_tuple(self):
        """Should accept tuple of strings."""
        validate_string_or_sequence(("a", "b"), "param")

    def test_invalid_list_with_int(self):
        """Should reject list containing non-strings."""
        with pytest.raises(ValidationError, match="should be strings"):
            validate_string_or_sequence(["a", 123], "param")

    def test_invalid_int(self):
        """Should reject integers."""
        with pytest.raises(
            ValidationError, match="should be a string or sequence"
        ):
            validate_string_or_sequence(123, "param")


class TestValidateLimit:
    """Tests for validate_limit."""

    def test_valid_limit(self):
        """Should accept valid limits."""
        validate_limit(25)
        validate_limit(0)
        validate_limit(1000)

    def test_invalid_type(self):
        """Should reject non-integers and booleans."""
        with pytest.raises(ValidationError, match="should be an integer"):
            validate_limit("25")  # type: ignore
        with pytest.raises(ValidationError, match="should be an integer"):
            validate_limit(True)  # type: ignore

    def test_limit_too_high(self):
        """Should reject limits over 1000."""
        with pytest.raises(ValidationError, match="between 0 and 1000"):
            validate_limit(1001)

    def test_negative_limit(self):
        """Should reject negative limits."""
        with pytest.raises(ValidationError, match="between 0 and 1000"):
            validate_limit(-1)


class TestValidateOffset:
    """Tests for validate_offset."""

    def test_valid_offset(self):
        """Should accept valid offsets."""
        validate_offset(0)
        validate_offset(100)

    def test_invalid_type(self):
        """Should reject non-integers and booleans."""
        with pytest.raises(ValidationError, match="should be an integer"):
            validate_offset("0")  # type: ignore
        with pytest.raises(ValidationError, match="should be an integer"):
            validate_offset(False)  # type: ignore

    def test_negative_offset(self):
        """Should reject negative offsets."""
        with pytest.raises(ValidationError, match="non-negative"):
            validate_offset(-1)


class TestValidateSortField:
    """Tests for validate_sort_field."""

    def test_valid_fields(self):
        """Should accept valid sort fields."""
        validate_sort_field(None)
        validate_sort_field("id")
        validate_sort_field("name")
        validate_sort_field("mindate")
        validate_sort_field("maxdate")
        validate_sort_field("datacoverage")

    def test_invalid_field(self):
        """Should reject invalid sort fields."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_sort_field("invalid")

    def test_invalid_type(self):
        """Should reject non-strings."""
        with pytest.raises(ValidationError, match="should be a string"):
            validate_sort_field(123)  # type: ignore


class TestValidateSortOrder:
    """Tests for validate_sort_order."""

    def test_valid_orders(self):
        """Should accept valid sort orders."""
        validate_sort_order("asc")
        validate_sort_order("desc")

    def test_invalid_order(self):
        """Should reject invalid sort orders."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_sort_order("ascending")

    def test_invalid_type(self):
        """Should reject non-strings."""
        with pytest.raises(ValidationError, match="should be a string"):
            validate_sort_order(123)  # type: ignore


class TestValidateUnits:
    """Tests for validate_units."""

    def test_valid_units(self):
        """Should accept valid units."""
        validate_units("metric")
        validate_units("standard")

    def test_invalid_units(self):
        """Should reject invalid units."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_units("imperial")

    def test_invalid_type(self):
        """Should reject non-strings."""
        with pytest.raises(ValidationError, match="should be a string"):
            validate_units(123)  # type: ignore


class TestValidateBoolean:
    """Tests for validate_boolean."""

    def test_valid_boolean(self):
        """Should accept booleans."""
        validate_boolean(True, "param")
        validate_boolean(False, "param")

    def test_invalid_int(self):
        """Should reject integers (even 0 and 1)."""
        with pytest.raises(ValidationError, match="should be a boolean"):
            validate_boolean(1, "param")

    def test_invalid_string(self):
        """Should reject strings."""
        with pytest.raises(ValidationError, match="should be a boolean"):
            validate_boolean("true", "param")


class TestWeatherValidators:
    """Tests for Weather API and helper validators."""

    def test_validate_non_empty_string(self):
        """Should validate non-empty strings."""
        from noaa.validators import validate_non_empty_string

        validate_non_empty_string("hello", "field")
        with pytest.raises(
            ValidationError, match="must be a non-empty string"
        ):
            validate_non_empty_string("", "field")
        with pytest.raises(
            ValidationError, match="must be a non-empty string"
        ):
            validate_non_empty_string("   ", "field")
        with pytest.raises(
            ValidationError, match="must be a non-empty string"
        ):
            validate_non_empty_string(None, "field")

    def test_validate_coordinates(self):
        """Should validate latitude and longitude within bounds."""
        from noaa.validators import validate_coordinates

        lat, lon = validate_coordinates(40.7128, -74.0060)
        assert lat == 40.7128
        assert lon == -74.0060

        with pytest.raises(ValidationError, match="numeric"):
            validate_coordinates("40.7", -74.0)
        with pytest.raises(ValidationError, match="numeric"):
            validate_coordinates(True, -74.0)
        with pytest.raises(ValidationError, match="latitude"):
            validate_coordinates(91.0, -74.0)
        with pytest.raises(ValidationError, match="latitude"):
            validate_coordinates(-91.0, -74.0)
        with pytest.raises(ValidationError, match="longitude"):
            validate_coordinates(40.0, 181.0)
        with pytest.raises(ValidationError, match="longitude"):
            validate_coordinates(40.0, -181.0)

    def test_validate_positive_int(self):
        """Should validate positive integers."""
        from noaa.validators import validate_positive_int

        validate_positive_int(0, "num", allow_zero=True)
        validate_positive_int(10, "num", allow_zero=False)

        with pytest.raises(ValidationError, match="integer"):
            validate_positive_int("10", "num")
        with pytest.raises(ValidationError, match="integer"):
            validate_positive_int(True, "num")
        with pytest.raises(ValidationError, match="non-negative"):
            validate_positive_int(-1, "num", allow_zero=True)
        with pytest.raises(ValidationError, match="greater than 0"):
            validate_positive_int(0, "num", allow_zero=False)

    def test_validate_weather_units(self):
        """Should validate us or si units."""
        from noaa.validators import validate_weather_units

        validate_weather_units(None)
        validate_weather_units("us")
        validate_weather_units("si")
        validate_weather_units("US")

        with pytest.raises(ValidationError, match="must be one of"):
            validate_weather_units("metric")
        with pytest.raises(ValidationError, match="must be one of"):
            validate_weather_units(123)  # type: ignore

    def test_validate_zone_type(self):
        """Should validate NWS zone types."""
        from noaa.validators import validate_zone_type

        validate_zone_type(None)
        validate_zone_type("forecast")
        validate_zone_type("land")
        validate_zone_type("marine")

        with pytest.raises(ValidationError, match="must be one of"):
            validate_zone_type("ocean")
        with pytest.raises(ValidationError, match="must be one of"):
            validate_zone_type(123)  # type: ignore
