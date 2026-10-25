"""Shared pytest fixtures for NOAA API tests."""

import json
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def api_token():
    """Return a test API token."""
    return "test-token-12345"


@pytest.fixture
def mock_response():
    """Factory fixture to create mock API responses."""

    def _create_response(data: dict):
        mock = MagicMock()
        mock.read.return_value = json.dumps(data).encode()
        mock.__enter__ = MagicMock(return_value=mock)
        mock.__exit__ = MagicMock(return_value=False)
        return mock

    return _create_response


@pytest.fixture
def sample_datasets_response():
    """Sample response for datasets endpoint."""
    return {
        "metadata": {"resultset": {"offset": 1, "count": 2, "limit": 25}},
        "results": [
            {
                "uid": "gov.noaa.ncdc:C00861",
                "id": "GHCND",
                "name": "Daily Summaries",
                "datacoverage": 1,
                "mindate": "1763-01-01",
                "maxdate": "2023-12-31",
            },
            {
                "uid": "gov.noaa.ncdc:C00946",
                "id": "GSOM",
                "name": "Global Summary of the Month",
                "datacoverage": 1,
                "mindate": "1763-01-01",
                "maxdate": "2023-12-31",
            },
        ],
    }


@pytest.fixture
def sample_stations_response():
    """Sample response for stations endpoint."""
    return {
        "metadata": {"resultset": {"offset": 1, "count": 1, "limit": 25}},
        "results": [
            {
                "elevation": 5.2,
                "mindate": "1948-01-01",
                "maxdate": "2023-12-31",
                "latitude": 40.7789,
                "name": "NY CITY CENTRAL PARK, NY US",
                "datacoverage": 1,
                "id": "GHCND:USW00094728",
                "longitude": -73.9692,
            }
        ],
    }


@pytest.fixture
def sample_data_response():
    """Sample response for data endpoint."""
    return {
        "metadata": {"resultset": {"offset": 1, "count": 2, "limit": 25}},
        "results": [
            {
                "date": "2023-01-01T00:00:00",
                "datatype": "TMAX",
                "station": "GHCND:USW00094728",
                "value": 12.2,
            },
            {
                "date": "2023-01-01T00:00:00",
                "datatype": "TMIN",
                "station": "GHCND:USW00094728",
                "value": 5.6,
            },
        ],
    }


@pytest.fixture
def noaa_client(api_token):
    """Create a NOAA client instance."""
    from noaa.client import NOAA

    return NOAA(api_token)
