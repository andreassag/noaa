"""Utility functions for the NOAA API client."""

import datetime
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Sequence, Union

from noaa.exceptions import APIError, ValidationError


def parse_date(
    date_value: Optional[Union[str, datetime.date, datetime.datetime]],
    name: str,
    include_time: bool = False,
) -> Optional[str]:
    """Parse and format a date value for the API.

    :param date_value: Date as string, date, or datetime object
    :param name: Name of the parameter (for error messages)
    :param include_time: Whether to include time component
    :return: Formatted date string or None
    """
    if date_value is None:
        return None

    if isinstance(date_value, datetime.datetime):
        dt = date_value
    elif isinstance(date_value, datetime.date):
        dt = datetime.datetime.combine(date_value, datetime.time.min)
    elif isinstance(date_value, str):
        try:
            dt = datetime.datetime.fromisoformat(date_value)
        except ValueError as error:
            raise ValidationError(
                f"{name} must be in ISO date format"
            ) from error
    else:
        raise ValidationError(f"{name} must be a string or datetime object")

    if include_time:
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    return dt.strftime("%Y-%m-%d")


def join_ids(value: Optional[Union[str, Sequence[str]]]) -> Optional[str]:
    """Join a sequence of IDs into an ampersand-separated string.

    :param value: Single ID or sequence of IDs
    :return: Joined string or original value
    """
    if isinstance(value, (list, tuple)):
        return "&".join(value)
    if isinstance(value, str) or value is None:
        return value
    return str(value)


def join_csv(value: Optional[Union[str, Sequence[str]]]) -> Optional[str]:
    """Join a sequence of strings into a comma-separated string.

    :param value: Single string or sequence of strings
    :return: Comma-separated string or original value
    """
    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)
    if isinstance(value, str) or value is None:
        return value
    return str(value)


def build_query_params(params: Dict[str, Any]) -> str:
    """Build URL query parameters from a dictionary.

    :param params: Dictionary of parameter names and values
    :return: URL-encoded query string
    """
    # Filter out None values
    filtered = {
        key: value for key, value in params.items() if value is not None
    }

    # URL encode, preserving ampersands in joined IDs
    encoded = urllib.parse.urlencode(filtered, safe="")
    return encoded.replace("%26", "&")


def make_api_request(
    url: str,
    headers: Dict[str, str],
    timeout: float = 30.0,
) -> dict:
    """Make a GET request to the API.

    :param url: Full URL including query parameters
    :param headers: Request headers
    :param timeout: Request timeout in seconds, defaults to 30.0
    :return: Parsed JSON response
    """
    request = urllib.request.Request(url=url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as err:
        error_msg = f"API request failed with status {err.code}: {err.reason}"
        try:
            payload = err.read()
            if payload:
                error_body = json.loads(payload.decode("utf-8"))
                if isinstance(error_body, dict):
                    detail = (
                        error_body.get("detail")
                        or error_body.get("message")
                        or error_body.get("error")
                    )
                    if detail:
                        error_msg = f"{error_msg} - {detail}"
        except Exception:
            pass
        raise APIError(error_msg, status_code=err.code) from err
    except urllib.error.URLError as err:
        raise APIError(f"Network error: {err.reason}") from err

    try:
        return json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise APIError("Invalid JSON response from API") from err
