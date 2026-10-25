"""Tests for utility functions."""

import datetime
from unittest.mock import MagicMock, patch

from noaa.exceptions import ValidationError
from noaa.utils import (
    build_query_params,
    join_ids,
    make_api_request,
    parse_date,
)

import pytest


class TestParseDate:
    """Tests for parse_date function."""

    def test_none_value(self):
        """Should return None for None input."""
        assert parse_date(None, "date") is None

    def test_valid_date_string(self):
        """Should parse valid ISO date strings."""
        result = parse_date("2023-01-15", "date")
        assert result == "2023-01-15"

    def test_valid_datetime_string(self):
        """Should parse valid ISO datetime strings."""
        result = parse_date("2023-01-15T10:30:00", "date")
        assert result == "2023-01-15"

    def test_valid_datetime_with_time(self):
        """Should include time when requested."""
        result = parse_date("2023-01-15T10:30:00", "date", include_time=True)
        assert result == "2023-01-15T10:30:00"

    def test_datetime_object(self):
        """Should accept datetime objects."""
        dt = datetime.datetime(2023, 1, 15, 10, 30, 0)
        result = parse_date(dt, "date")
        assert result == "2023-01-15"

    def test_date_object(self):
        """Should accept date objects."""
        d = datetime.date(2023, 1, 15)
        result = parse_date(d, "date")
        assert result == "2023-01-15"

    def test_datetime_object_with_time(self):
        """Should include time from datetime objects when requested."""
        dt = datetime.datetime(2023, 1, 15, 10, 30, 45)
        result = parse_date(dt, "date", include_time=True)
        assert result == "2023-01-15T10:30:45"

    def test_invalid_format(self):
        """Should raise error for invalid date format."""
        with pytest.raises(ValidationError, match="ISO date format"):
            parse_date("01-15-2023", "date")

    def test_invalid_type(self):
        """Should raise error for invalid type."""
        with pytest.raises(ValidationError, match="string or datetime"):
            parse_date(123, "date")  # type: ignore


class TestJoinIds:
    """Tests for join_ids function."""

    def test_none_value(self):
        """Should return None for None input."""
        assert join_ids(None) is None

    def test_string_value(self):
        """Should return string unchanged."""
        assert join_ids("GHCND") == "GHCND"

    def test_list_value(self):
        """Should join list with ampersands."""
        result = join_ids(["GHCND", "GSOM", "GSOY"])
        assert result == "GHCND&GSOM&GSOY"

    def test_tuple_value(self):
        """Should join tuple with ampersands."""
        result = join_ids(("GHCND", "GSOM"))
        assert result == "GHCND&GSOM"

    def test_empty_list(self):
        """Should return empty string for empty list."""
        assert join_ids([]) == ""

    def test_other_value(self):
        """Should stringify other values."""
        assert join_ids(123) == "123"  # type: ignore


class TestJoinCsv:
    """Tests for join_csv function."""

    def test_none_value(self):
        """Should return None for None input."""
        from noaa.utils import join_csv

        assert join_csv(None) is None

    def test_string_value(self):
        """Should return string unchanged."""
        from noaa.utils import join_csv

        assert join_csv("CA") == "CA"

    def test_list_value(self):
        """Should join list with commas."""
        from noaa.utils import join_csv

        assert join_csv(["CA", "NV", "OR"]) == "CA,NV,OR"

    def test_tuple_value(self):
        """Should join tuple with commas."""
        from noaa.utils import join_csv

        assert join_csv(("CA", "NV")) == "CA,NV"

    def test_other_value(self):
        """Should stringify other values."""
        from noaa.utils import join_csv

        assert join_csv(456) == "456"  # type: ignore


class TestBuildQueryParams:
    """Tests for build_query_params function."""

    def test_empty_params(self):
        """Should return empty string for empty dict."""
        assert build_query_params({}) == ""

    def test_filters_none_values(self):
        """Should filter out None values."""
        params = {"a": "1", "b": None, "c": "3"}
        result = build_query_params(params)
        assert "a=1" in result
        assert "c=3" in result
        assert "b" not in result

    def test_encodes_special_characters(self):
        """Should URL encode special characters."""
        params = {"location": "NY US"}
        result = build_query_params(params)
        assert "location=NY+US" in result or "location=NY%20US" in result

    def test_preserves_ampersands(self):
        """Should preserve ampersands in values."""
        params = {"ids": "A&B&C"}
        result = build_query_params(params)
        assert "ids=A&B&C" in result


class TestMakeApiRequest:
    """Tests for make_api_request function."""

    def test_successful_request(self, mock_response):
        """Should return parsed JSON response."""
        expected_data = {"results": [1, 2, 3]}
        mock = mock_response(expected_data)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = make_api_request("http://test.com", {"token": "abc"})

        assert result == expected_data

    def test_request_headers(self, mock_response):
        """Should pass headers to request."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                make_api_request("http://test.com", {"token": "abc"})

                mock_request.assert_called_once()
                call_kwargs = mock_request.call_args[1]
                assert call_kwargs["headers"] == {"token": "abc"}
                assert call_kwargs["method"] == "GET"

    def test_http_error_with_json_body(self):
        """Should raise APIError with status code and detail on HTTPError."""
        import io
        import urllib.error

        error_fp = io.BytesIO(b'{"detail": "Station not found"}')
        http_err = urllib.error.HTTPError(
            url="http://test.com",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=error_fp,
        )

        with patch("noaa.utils.urllib.request.urlopen", side_effect=http_err):
            from noaa.exceptions import APIError

            with pytest.raises(APIError) as exc_info:
                make_api_request("http://test.com", {})

            assert exc_info.value.status_code == 404
            assert "Station not found" in str(exc_info.value)

    def test_http_error_without_json_body(self):
        """Should raise APIError when HTTPError body is empty or non-JSON."""
        import io
        import urllib.error

        error_fp = io.BytesIO(b"Gateway Timeout")
        http_err = urllib.error.HTTPError(
            url="http://test.com",
            code=504,
            msg="Gateway Timeout",
            hdrs={},
            fp=error_fp,
        )

        with patch("noaa.utils.urllib.request.urlopen", side_effect=http_err):
            from noaa.exceptions import APIError

            with pytest.raises(APIError) as exc_info:
                make_api_request("http://test.com", {})

            assert exc_info.value.status_code == 504
            assert "504" in str(exc_info.value)

    def test_network_error_raises_api_error(self):
        """Should raise APIError on URLError network failures."""
        import urllib.error

        url_err = urllib.error.URLError("Connection refused")

        with patch("noaa.utils.urllib.request.urlopen", side_effect=url_err):
            from noaa.exceptions import APIError

            with pytest.raises(
                APIError, match="Network error: Connection refused"
            ):
                make_api_request("http://test.com", {})

    def test_invalid_json_raises_api_error(self):
        """Should raise APIError when server returns invalid JSON."""
        mock = MagicMock()
        mock.read.return_value = b"<html>Not JSON</html>"
        mock.__enter__ = MagicMock(return_value=mock)
        mock.__exit__ = MagicMock(return_value=False)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            from noaa.exceptions import APIError

            with pytest.raises(APIError, match="Invalid JSON"):
                make_api_request("http://test.com", {})
