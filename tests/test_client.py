"""Tests for the NOAA API client."""

from unittest.mock import MagicMock, patch

from noaa.client import NOAA, Climate
from noaa.exceptions import ValidationError

import pytest


class TestNOAAInit:
    """Tests for NOAA/Climate client initialization."""

    def test_valid_token(self):
        """Should accept valid token."""
        client = NOAA("valid-token")
        assert client._headers == {"token": "valid-token"}
        assert client.timeout == 30.0

    def test_climate_alias(self):
        """Climate and NOAA should be identical."""
        assert Climate is NOAA
        client = Climate("valid-token", timeout=12.5)
        assert client.timeout == 12.5

    def test_empty_token(self):
        """Should reject empty token."""
        with pytest.raises(ValidationError, match="non-empty string"):
            NOAA("")

    def test_none_token(self):
        """Should reject None token."""
        with pytest.raises(ValidationError, match="non-empty string"):
            NOAA(None)  # type: ignore

    def test_invalid_token_type(self):
        """Should reject non-string token."""
        with pytest.raises(ValidationError, match="non-empty string"):
            NOAA(12345)  # type: ignore

    def test_invalid_timeout(self):
        """Should reject invalid timeout values."""
        with pytest.raises(ValidationError, match="timeout"):
            NOAA("valid-token", timeout=-1)
        with pytest.raises(ValidationError, match="timeout"):
            NOAA("valid-token", timeout=0)
        with pytest.raises(ValidationError, match="timeout"):
            NOAA("valid-token", timeout=True)  # type: ignore


class TestGetDatasets:
    """Tests for get_datasets method."""

    def test_get_all_datasets(
        self, noaa_client, mock_response, sample_datasets_response
    ):
        """Should fetch all datasets."""
        mock = mock_response(sample_datasets_response)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = noaa_client.get_datasets()

        assert result == sample_datasets_response
        assert len(result["results"]) == 2

    def test_get_specific_dataset(self, noaa_client, mock_response):
        """Should fetch specific dataset by ID."""
        response_data = {"id": "GHCND", "name": "Daily Summaries"}
        mock = mock_response(response_data)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_datasets(dataset_id="GHCND")

                call_args = mock_request.call_args[1]
                assert "datasets/GHCND" in call_args["url"]

    def test_invalid_dataset_id_type(self, noaa_client):
        """Should reject non-string dataset_id."""
        with pytest.raises(ValidationError):
            noaa_client.get_datasets(dataset_id=123)

    def test_with_filters(
        self, noaa_client, mock_response, sample_datasets_response
    ):
        """Should include filter parameters."""
        mock = mock_response(sample_datasets_response)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_datasets(
                    start_date="2020-01-01", end_date="2023-12-31", limit=50
                )

                call_args = mock_request.call_args[1]
                assert "startdate=2020-01-01" in call_args["url"]
                assert "enddate=2023-12-31" in call_args["url"]
                assert "limit=50" in call_args["url"]


class TestGetDataCategories:
    """Tests for get_data_categories method."""

    def test_get_all_categories(self, noaa_client, mock_response):
        """Should fetch all data categories."""
        response_data = {"results": [{"id": "TEMP", "name": "Temperature"}]}
        mock = mock_response(response_data)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = noaa_client.get_data_categories()

        assert result == response_data

    def test_get_specific_category(self, noaa_client, mock_response):
        """Should fetch specific category."""
        mock = mock_response({"id": "TEMP"})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_data_categories(category_id="TEMP")

                call_args = mock_request.call_args[1]
                assert "datacategories/TEMP" in call_args["url"]


class TestGetDataTypes:
    """Tests for get_data_types method."""

    def test_get_all_types(self, noaa_client, mock_response):
        """Should fetch all data types."""
        response_data = {"results": [{"id": "TMAX"}, {"id": "TMIN"}]}
        mock = mock_response(response_data)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = noaa_client.get_data_types()

        assert len(result["results"]) == 2

    def test_with_category_filter(self, noaa_client, mock_response):
        """Should filter by data category."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_data_types(data_category_id="TEMP")

                call_args = mock_request.call_args[1]
                assert "datacategoryid=TEMP" in call_args["url"]


class TestGetLocationCategories:
    """Tests for get_location_categories method."""

    def test_get_all_location_categories(self, noaa_client, mock_response):
        """Should fetch all location categories."""
        response_data = {"results": [{"id": "CITY"}, {"id": "ST"}]}
        mock = mock_response(response_data)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = noaa_client.get_location_categories()

        assert len(result["results"]) == 2


class TestGetLocations:
    """Tests for get_locations method."""

    def test_get_all_locations(self, noaa_client, mock_response):
        """Should fetch all locations."""
        response_data = {
            "results": [{"id": "FIPS:37", "name": "North Carolina"}]
        }
        mock = mock_response(response_data)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = noaa_client.get_locations()

        assert result == response_data

    def test_with_location_category(self, noaa_client, mock_response):
        """Should filter by location category."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_locations(location_category_id="ST")

                call_args = mock_request.call_args[1]
                assert "locationcategoryid=ST" in call_args["url"]


class TestGetStations:
    """Tests for get_stations method."""

    def test_get_all_stations(
        self, noaa_client, mock_response, sample_stations_response
    ):
        """Should fetch all stations."""
        mock = mock_response(sample_stations_response)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = noaa_client.get_stations()

        assert result == sample_stations_response

    def test_with_extent(self, noaa_client, mock_response):
        """Should include extent parameter."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_stations(extent="40,-74,41,-73")

                call_args = mock_request.call_args[1]
                assert "extent=" in call_args["url"]

    def test_with_multiple_ids(self, noaa_client, mock_response):
        """Should handle multiple dataset IDs."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_stations(dataset_id=["GHCND", "GSOM"])

                call_args = mock_request.call_args[1]
                assert "datasetid=GHCND&GSOM" in call_args["url"]


class TestGetData:
    """Tests for get_data method."""

    def test_get_data(self, noaa_client, mock_response, sample_data_response):
        """Should fetch climate data."""
        mock = mock_response(sample_data_response)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            result = noaa_client.get_data(
                dataset_id="GHCND",
                start_date="2023-01-01",
                end_date="2023-01-31",
            )

        assert result == sample_data_response
        assert len(result["results"]) == 2

    def test_includes_time_in_dates(self, noaa_client, mock_response):
        """Should include time component in date parameters."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_data(
                    dataset_id="GHCND",
                    start_date="2023-01-01",
                    end_date="2023-01-31",
                )

                call_args = mock_request.call_args[1]
                # Time is URL-encoded, so colons become %3A
                assert "T00%3A00%3A00" in call_args["url"]

    def test_with_units(self, noaa_client, mock_response):
        """Should include units parameter."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_data(
                    dataset_id="GHCND",
                    start_date="2023-01-01",
                    end_date="2023-01-31",
                    units="standard",
                )

                call_args = mock_request.call_args[1]
                assert "units=standard" in call_args["url"]

    def test_with_include_metadata(self, noaa_client, mock_response):
        """Should include metadata parameter when True."""
        mock = mock_response({"results": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_request:
                mock_request.return_value = MagicMock()
                noaa_client.get_data(
                    dataset_id="GHCND",
                    start_date="2023-01-01",
                    end_date="2023-01-31",
                    include_metadata=True,
                )

                call_args = mock_request.call_args[1]
                assert "includemetadata=" in call_args["url"]

    def test_get_data_required_args(self, noaa_client):
        """Should require dataset_id, start_date, and end_date."""
        with pytest.raises(ValidationError, match="dataset_id"):
            noaa_client.get_data(
                dataset_id="", start_date="2023-01-01", end_date="2023-01-31"
            )
        with pytest.raises(ValidationError, match="start_date"):
            noaa_client.get_data(
                dataset_id="GHCND",
                start_date=None,
                end_date="2023-01-31",  # type: ignore
            )
        with pytest.raises(ValidationError, match="end_date"):
            noaa_client.get_data(
                dataset_id="GHCND",
                start_date="2023-01-01",
                end_date=None,  # type: ignore
            )


class TestRequestValidation:
    """Tests for request parameter validation."""

    def test_invalid_limit(self, noaa_client):
        """Should reject invalid limit."""
        with pytest.raises(ValidationError):
            noaa_client.get_datasets(limit=2000)

    def test_invalid_sort_field(self, noaa_client):
        """Should reject invalid sort field."""
        with pytest.raises(ValidationError):
            noaa_client.get_datasets(sort_field="invalid")

    def test_invalid_sort_order(self, noaa_client):
        """Should reject invalid sort order."""
        with pytest.raises(ValidationError):
            noaa_client.get_datasets(sort_order="ascending")

    def test_invalid_date_format(self, noaa_client):
        """Should reject invalid date format."""
        with pytest.raises(ValidationError):
            noaa_client.get_datasets(start_date="01-01-2023")
