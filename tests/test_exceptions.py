"""Tests for custom exceptions."""

from noaa.exceptions import APIError, NOAAException, ValidationError

import pytest


class TestExceptions:
    """Tests for exception hierarchy."""

    def test_validation_error_is_noaa_exception(self):
        """ValidationError should inherit from NOAAException."""
        assert issubclass(ValidationError, NOAAException)

    def test_api_error_is_noaa_exception(self):
        """APIError should inherit from NOAAException."""
        assert issubclass(APIError, NOAAException)

    def test_noaa_exception_is_exception(self):
        """NOAAException should inherit from Exception."""
        assert issubclass(NOAAException, Exception)

    def test_can_catch_with_base_exception(self):
        """Should be able to catch all NOAA errors with base class."""
        with pytest.raises(NOAAException):
            raise ValidationError("test error")

    def test_exception_message(self):
        """Should preserve error message."""
        error = ValidationError("custom message")
        assert str(error) == "custom message"

    def test_api_error_status_code(self):
        """APIError should store optional status_code."""
        error = APIError("Not Found", status_code=404)
        assert str(error) == "Not Found"
        assert error.status_code == 404
