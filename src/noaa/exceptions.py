"""Custom exceptions for the NOAA API client."""

from typing import Optional


class NOAAException(Exception):
    """Base exception for NOAA API errors."""

    pass


class ValidationError(NOAAException):
    """Raised when input validation fails."""

    pass


class APIError(NOAAException):
    """Raised when the API returns an error."""

    def __init__(
        self, message: str, status_code: Optional[int] = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
