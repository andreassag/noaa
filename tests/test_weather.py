"""Tests for the NOAA Weather (NWS) API client."""

import datetime
from unittest.mock import MagicMock, patch

from noaa.exceptions import ValidationError
from noaa.weather import API, Weather

import pytest


class TestWeatherInit:
    """Tests for Weather client initialization."""

    def test_default_init(self):
        """Should initialize with default user agent and timeout."""
        client = Weather()
        assert "noaa-python-client" in client.user_agent
        assert client.timeout == 30.0
        assert client._headers["User-Agent"] == client.user_agent
        assert client._headers["Accept"] == "application/geo+json"

    def test_custom_user_agent_and_timeout(self):
        """Should accept custom user agent and timeout."""
        client = Weather(
            user_agent="my-app (contact@example.com)", timeout=15.5
        )
        assert client.user_agent == "my-app (contact@example.com)"
        assert client.timeout == 15.5
        assert client._headers["User-Agent"] == "my-app (contact@example.com)"

    def test_api_alias(self):
        """API should be an alias for Weather."""
        assert API is Weather
        client = API()
        assert isinstance(client, Weather)

    def test_invalid_user_agent(self):
        """Should reject empty or non-string user agent."""
        with pytest.raises(ValidationError, match="user_agent"):
            Weather(user_agent="")
        with pytest.raises(ValidationError, match="user_agent"):
            Weather(user_agent="   ")
        with pytest.raises(ValidationError, match="user_agent"):
            Weather(user_agent=None)  # type: ignore

    def test_invalid_timeout(self):
        """Should reject invalid timeout values."""
        with pytest.raises(ValidationError, match="timeout"):
            Weather(timeout=0)
        with pytest.raises(ValidationError, match="timeout"):
            Weather(timeout=-5)
        with pytest.raises(ValidationError, match="timeout"):
            Weather(timeout=True)  # type: ignore
        with pytest.raises(ValidationError, match="timeout"):
            Weather(timeout="30")  # type: ignore


class TestWeatherPointsAndForecast:
    """Tests for points and forecast endpoints."""

    def test_get_points(self, mock_response):
        """Should request points endpoint with 4-decimal coordinates."""
        client = Weather()
        fake_data = {"properties": {"cwa": "OKX", "gridX": 33, "gridY": 35}}
        mock = mock_response(fake_data)

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                res = client.get_points(40.712776, -74.005974)
                assert res == fake_data
                url = mock_req.call_args[1]["url"]
                assert "points/40.7128,-74.0060" in url

    def test_get_points_invalid_coords(self):
        """Should reject out-of-bounds or non-numeric coordinates."""
        client = Weather()
        with pytest.raises(ValidationError, match="latitude"):
            client.get_points(95.0, -74.0)
        with pytest.raises(ValidationError, match="longitude"):
            client.get_points(40.0, -185.0)
        with pytest.raises(ValidationError, match="latitude"):
            client.get_points("40.0", -74.0)  # type: ignore

    def test_get_point_stations(self, mock_response):
        """Should request stations endpoint for given points."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_point_stations(39.7392, -104.9903)
                url = mock_req.call_args[1]["url"]
                assert "points/39.7392,-104.9903/stations" in url

    def test_get_gridpoint(self, mock_response):
        """Should fetch numerical data for gridpoint."""
        client = Weather()
        mock = mock_response({"properties": {}})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_gridpoint("okx", 33, 35)
                url = mock_req.call_args[1]["url"]
                assert "gridpoints/OKX/33,35" in url

    def test_get_gridpoint_forecast(self, mock_response):
        """Should fetch forecast for gridpoint with optional units."""
        client = Weather()
        mock = mock_response({"properties": {"periods": []}})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_gridpoint_forecast("okx", 33, 35, units="us")
                url = mock_req.call_args[1]["url"]
                assert "gridpoints/OKX/33,35/forecast" in url
                assert "units=us" in url

    def test_get_gridpoint_forecast_hourly(self, mock_response):
        """Should fetch hourly forecast for gridpoint."""
        client = Weather()
        mock = mock_response({"properties": {"periods": []}})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_gridpoint_forecast_hourly("okx", 33, 35, units="si")
                url = mock_req.call_args[1]["url"]
                assert "gridpoints/OKX/33,35/forecast/hourly" in url
                assert "units=si" in url

    def test_get_forecast_via_point_metadata(self, mock_response):
        """Should resolve forecast URL through points endpoint."""
        client = Weather()
        point_data = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/OKX/33,35/forecast",
                "forecastHourly": "https://api.weather.gov/gridpoints/OKX/33,35/forecast/hourly",
            }
        }
        forecast_data = {"properties": {"periods": [{"name": "Today"}]}}

        mock_point = mock_response(point_data)
        mock_forecast = mock_response(forecast_data)

        with patch(
            "noaa.utils.urllib.request.urlopen",
            side_effect=[mock_point, mock_forecast],
        ):
            res = client.get_forecast(40.7128, -74.0060, hourly=False)
            assert res == forecast_data

    def test_get_forecast_hourly(self, mock_response):
        """Should fetch hourly forecast when hourly=True."""
        client = Weather()
        point_data = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/OKX/33,35/forecast",
                "forecastHourly": "https://api.weather.gov/gridpoints/OKX/33,35/forecast/hourly",
            }
        }
        forecast_data = {"properties": {"periods": [{"name": "1 PM"}]}}

        mock_point = mock_response(point_data)
        mock_forecast = mock_response(forecast_data)

        with patch(
            "noaa.utils.urllib.request.urlopen",
            side_effect=[mock_point, mock_forecast],
        ):
            res = client.get_forecast(
                40.7128, -74.0060, hourly=True, units="si"
            )
            assert res == forecast_data

    def test_get_forecast_fallback_to_cwa_and_grid(self, mock_response):
        """Should fallback to gridpoint forecast if forecast URL missing."""
        client = Weather()
        point_data = {
            "properties": {
                "cwa": "OKX",
                "gridX": 33,
                "gridY": 35,
            }
        }
        forecast_data = {"properties": {"periods": []}}

        mock_point = mock_response(point_data)
        mock_forecast = mock_response(forecast_data)

        with patch(
            "noaa.utils.urllib.request.urlopen",
            side_effect=[mock_point, mock_forecast],
        ):
            res = client.get_forecast(40.7128, -74.0060, hourly=False)
            assert res == forecast_data

    def test_get_forecast_unresolvable_error(self, mock_response):
        """Should raise ValidationError if forecast cannot be resolved."""
        client = Weather()
        point_data = {"properties": {}}
        mock_point = mock_response(point_data)

        with patch(
            "noaa.utils.urllib.request.urlopen", return_value=mock_point
        ):
            with pytest.raises(ValidationError, match="Unable to resolve"):
                client.get_forecast(40.7128, -74.0060)


class TestWeatherAlerts:
    """Tests for weather alerts endpoints."""

    def test_get_alerts_filters(self, mock_response):
        """Should pass alert query filters cleanly."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_alerts(
                    active=True,
                    area=["CA", "NV"],
                    severity="severe",
                    limit=5,
                )
                url = mock_req.call_args[1]["url"]
                assert "alerts/active" in url
                assert "area=CA%2CNV" in url or "area=CA,NV" in url
                assert "severity=severe" in url
                assert "limit=5" in url

    def test_get_active_alerts(self, mock_response):
        """get_active_alerts should call alerts/active."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_active_alerts(area="CA")
                url = mock_req.call_args[1]["url"]
                assert "alerts/active" in url
                assert "area=CA" in url

    def test_get_alert_by_id(self, mock_response):
        """Should request alert by ID."""
        client = Weather()
        mock = mock_response({"id": "urn:oid:alert-123"})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_alert("alert-123")
                url = mock_req.call_args[1]["url"]
                assert "alerts/alert-123" in url

    def test_get_active_alerts_count(self, mock_response):
        """Should request alert count endpoint."""
        client = Weather()
        mock = mock_response({"total": 42})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_active_alerts_count()
                url = mock_req.call_args[1]["url"]
                assert "alerts/active/count" in url

    def test_get_active_alerts_by_zone(self, mock_response):
        """Should request active alerts by zone."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_active_alerts_by_zone("caz006")
                url = mock_req.call_args[1]["url"]
                assert "alerts/active/zone/CAZ006" in url

    def test_get_active_alerts_by_area(self, mock_response):
        """Should request active alerts by area."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_active_alerts_by_area("ca")
                url = mock_req.call_args[1]["url"]
                assert "alerts/active/area/CA" in url


class TestWeatherStationsAndObservations:
    """Tests for stations and observations endpoints."""

    def test_get_stations_collection(self, mock_response):
        """Should request stations collection with state filter."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_stations(state=["NY", "NJ"], limit=10)
                url = mock_req.call_args[1]["url"]
                assert "stations" in url
                assert "state=NY%2CNJ" in url or "state=NY,NJ" in url
                assert "limit=10" in url

    def test_get_single_station(self, mock_response):
        """Should request single station by ID."""
        client = Weather()
        mock = mock_response({"properties": {"stationIdentifier": "KJFK"}})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_stations(station_id="kjfk")
                url = mock_req.call_args[1]["url"]
                assert "stations/KJFK" in url

    def test_get_station_observations(self, mock_response):
        """Should request observations for a station with start/end."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_station_observations(
                    "kjfk",
                    start=datetime.date(2023, 1, 1),
                    end="2023-01-02T12:00:00",
                    limit=20,
                )
                url = mock_req.call_args[1]["url"]
                assert "stations/KJFK/observations" in url
                assert "start=2023-01-01" in url
                assert "limit=20" in url

    def test_get_latest_observation(self, mock_response):
        """Should request latest observation for a station."""
        client = Weather()
        mock = mock_response({"properties": {}})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_latest_observation("kjfk", require_qc=True)
                url = mock_req.call_args[1]["url"]
                assert "stations/KJFK/observations/latest" in url
                assert "require_qc=true" in url


class TestWeatherZonesOfficesGlossary:
    """Tests for zones, offices, and glossary endpoints."""

    def test_get_zones(self, mock_response):
        """Should query zones endpoint."""
        client = Weather()
        mock = mock_response({"features": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_zones(zone_type="forecast", area="CA", limit=10)
                url = mock_req.call_args[1]["url"]
                assert "zones/forecast" in url
                assert "area=CA" in url

    def test_get_single_zone(self, mock_response):
        """Should query a single zone by ID."""
        client = Weather()
        mock = mock_response({"properties": {}})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_zones(zone_type="forecast", zone_id="CAZ006")
                url = mock_req.call_args[1]["url"]
                assert "zones/forecast/CAZ006" in url

    def test_get_zone_forecast(self, mock_response):
        """Should query forecast for a zone."""
        client = Weather()
        mock = mock_response({"properties": {}})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_zone_forecast("public", "caz006")
                url = mock_req.call_args[1]["url"]
                assert "zones/public/CAZ006/forecast" in url

    def test_get_office(self, mock_response):
        """Should query office metadata."""
        client = Weather()
        mock = mock_response({"name": "New York, NY"})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_office("okx")
                url = mock_req.call_args[1]["url"]
                assert "offices/OKX" in url

    def test_get_glossary(self, mock_response):
        """Should query glossary terms."""
        client = Weather()
        mock = mock_response({"glossary": []})

        with patch("noaa.utils.urllib.request.urlopen", return_value=mock):
            with patch("noaa.utils.urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                client.get_glossary()
                url = mock_req.call_args[1]["url"]
                assert "glossary" in url
