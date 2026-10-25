"""NOAA National Weather Service (NWS) API client."""

import datetime
import urllib.parse
from typing import Any, Dict, Optional, Sequence, Union

from noaa.exceptions import ValidationError
from noaa.utils import (
    build_query_params,
    join_csv,
    make_api_request,
    parse_date,
)
from noaa.validators import (
    validate_boolean,
    validate_coordinates,
    validate_non_empty_string,
    validate_positive_int,
    validate_weather_units,
    validate_zone_type,
)

IdType = Optional[Union[str, Sequence[str]]]
DateType = Optional[Union[str, datetime.date, datetime.datetime]]


class Weather:
    """Client for interfacing with NOAA's National Weather Service (NWS) API.

    Docs: https://www.weather.gov/documentation/services-web-api
    API root: https://api.weather.gov/

    :param user_agent: User-Agent header (required by NWS specification)
    :type user_agent: str
    :param timeout: Request timeout in seconds, defaults to 30.0
    :type timeout: float
    """

    BASE_URL = "https://api.weather.gov/"

    def __init__(
        self,
        user_agent: str = (
            "noaa-python-client (https://github.com/andreassag/noaa)"
        ),
        timeout: float = 30.0,
    ) -> None:
        validate_non_empty_string(user_agent, "user_agent")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise ValidationError("timeout must be a positive number")

        self.user_agent = user_agent
        self.timeout = float(timeout)
        self._headers = {
            "User-Agent": user_agent,
            "Accept": "application/geo+json",
        }

    def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Internal helper to make requests against api.weather.gov."""
        query_string = build_query_params(params) if params else ""
        url = urllib.parse.urljoin(self.BASE_URL, endpoint)
        full_url = f"{url}?{query_string}" if query_string else url
        return make_api_request(full_url, self._headers, timeout=self.timeout)

    # -------------------------------------------------------------------------
    # Points & Forecast Endpoints
    # -------------------------------------------------------------------------

    def get_points(
        self,
        latitude: Union[float, int],
        longitude: Union[float, int],
    ) -> dict:
        """Get gridpoint and forecast metadata for given coordinates.

        :param latitude: Latitude (-90 to 90)
        :param longitude: Longitude (-180 to 180)
        :return: Point metadata response dictionary
        """
        lat, lon = validate_coordinates(latitude, longitude)
        endpoint = f"points/{lat:.4f},{lon:.4f}"
        return self._request(endpoint)

    def get_point_stations(
        self,
        latitude: Union[float, int],
        longitude: Union[float, int],
    ) -> dict:
        """Get observation stations near coordinates.

        :param latitude: Latitude (-90 to 90)
        :param longitude: Longitude (-180 to 180)
        :return: Observation stations collection dictionary
        """
        lat, lon = validate_coordinates(latitude, longitude)
        endpoint = f"points/{lat:.4f},{lon:.4f}/stations"
        return self._request(endpoint)

    def get_gridpoint(
        self,
        office: str,
        grid_x: int,
        grid_y: int,
    ) -> dict:
        """Get raw numerical forecast data for a gridpoint.

        :param office: WFO (Weather Forecast Office) ID (e.g. 'OKX')
        :param grid_x: Grid X coordinate
        :param grid_y: Grid Y coordinate
        :return: Gridpoint data dictionary
        """
        validate_non_empty_string(office, "office")
        validate_positive_int(grid_x, "grid_x", allow_zero=True)
        validate_positive_int(grid_y, "grid_y", allow_zero=True)
        endpoint = f"gridpoints/{office.upper()}/{grid_x},{grid_y}"
        return self._request(endpoint)

    def get_gridpoint_forecast(
        self,
        office: str,
        grid_x: int,
        grid_y: int,
        units: Optional[str] = None,
    ) -> dict:
        """Get 12-hour textual forecast for a gridpoint.

        :param office: WFO ID
        :param grid_x: Grid X coordinate
        :param grid_y: Grid Y coordinate
        :param units: 'us' or 'si' units, defaults to None
        :return: Forecast dictionary
        """
        validate_non_empty_string(office, "office")
        validate_positive_int(grid_x, "grid_x", allow_zero=True)
        validate_positive_int(grid_y, "grid_y", allow_zero=True)
        validate_weather_units(units)
        params: Dict[str, Any] = {}
        if units:
            params["units"] = units.lower()
        endpoint = f"gridpoints/{office.upper()}/{grid_x},{grid_y}/forecast"
        return self._request(endpoint, params=params)

    def get_gridpoint_forecast_hourly(
        self,
        office: str,
        grid_x: int,
        grid_y: int,
        units: Optional[str] = None,
    ) -> dict:
        """Get hourly forecast for a gridpoint.

        :param office: WFO ID
        :param grid_x: Grid X coordinate
        :param grid_y: Grid Y coordinate
        :param units: 'us' or 'si' units, defaults to None
        :return: Hourly forecast dictionary
        """
        validate_non_empty_string(office, "office")
        validate_positive_int(grid_x, "grid_x", allow_zero=True)
        validate_positive_int(grid_y, "grid_y", allow_zero=True)
        validate_weather_units(units)
        params: Dict[str, Any] = {}
        if units:
            params["units"] = units.lower()
        endpoint = (
            f"gridpoints/{office.upper()}/{grid_x},{grid_y}/forecast/hourly"
        )
        return self._request(endpoint, params=params)

    def get_forecast(
        self,
        latitude: Union[float, int],
        longitude: Union[float, int],
        hourly: bool = False,
        units: Optional[str] = None,
    ) -> dict:
        """Convenience method: get forecast by coordinates.

        Resolves gridpoint metadata first via `get_points`, then fetches
        either the 7-day regular or hourly forecast.

        :param latitude: Latitude (-90 to 90)
        :param longitude: Longitude (-180 to 180)
        :param hourly: If True, fetch hourly forecast, defaults to False
        :param units: 'us' or 'si' units, defaults to None
        :return: Forecast dictionary
        """
        validate_boolean(hourly, "hourly")
        validate_weather_units(units)
        points = self.get_points(latitude, longitude)
        props = points.get("properties", {})
        forecast_url = (
            props.get("forecastHourly") if hourly else props.get("forecast")
        )

        if not forecast_url:
            cwa = props.get("cwa")
            grid_x = props.get("gridX")
            grid_y = props.get("gridY")
            if cwa and grid_x is not None and grid_y is not None:
                if hourly:
                    return self.get_gridpoint_forecast_hourly(
                        cwa, grid_x, grid_y, units=units
                    )
                return self.get_gridpoint_forecast(
                    cwa, grid_x, grid_y, units=units
                )
            raise ValidationError(
                "Unable to resolve forecast URL from point coordinates"
            )

        parsed = urllib.parse.urlparse(forecast_url)
        params: Dict[str, Any] = {}
        if units:
            params["units"] = units.lower()
        query_string = build_query_params(params) if params else ""
        full_url = (
            f"{forecast_url}?{query_string}" if query_string else forecast_url
        )

        # Check if forecast_url is absolute or path
        if parsed.scheme:
            return make_api_request(
                full_url, self._headers, timeout=self.timeout
            )
        return self._request(forecast_url.lstrip("/"), params=params)

    # -------------------------------------------------------------------------
    # Alerts Endpoints
    # -------------------------------------------------------------------------

    def get_alerts(
        self,
        active: Optional[bool] = None,
        start: DateType = None,
        end: DateType = None,
        status: IdType = None,
        message_type: IdType = None,
        event: IdType = None,
        code: IdType = None,
        area: IdType = None,
        point: Optional[str] = None,
        region: IdType = None,
        region_type: Optional[str] = None,
        zone: IdType = None,
        urgency: IdType = None,
        severity: IdType = None,
        certainty: IdType = None,
        limit: Optional[int] = None,
    ) -> dict:
        """Get weather alerts with optional filters.

        :param active: Filter by active status
        :param start: Start time
        :param end: End time
        :param status: Filter by alert status (e.g. 'actual')
        :param message_type: Filter by message type (e.g. 'alert')
        :param event: Filter by event name
        :param code: Filter by event code
        :param area: State/territory two-letter code(s) (e.g. 'CA', 'TX')
        :param point: Coordinates as 'lat,lon'
        :param region: Marine or land region code(s)
        :param region_type: Region type ('land' or 'marine')
        :param zone: Zone ID(s) (e.g. 'CAZ006')
        :param urgency: Filter by urgency
        :param severity: Filter by severity
        :param certainty: Filter by certainty
        :param limit: Result limit (positive int)
        :return: Alerts GeoJSON FeatureCollection dictionary
        """
        endpoint = "alerts/active" if active else "alerts"
        if active is not None:
            validate_boolean(active, "active")
        if limit is not None:
            validate_positive_int(limit, "limit", allow_zero=False)

        parsed_start = parse_date(start, "start", include_time=True)
        parsed_end = parse_date(end, "end", include_time=True)

        params: Dict[str, Any] = {
            "start": parsed_start,
            "end": parsed_end,
            "status": join_csv(status),
            "message_type": join_csv(message_type),
            "event": join_csv(event),
            "code": join_csv(code),
            "area": join_csv(area),
            "point": point,
            "region": join_csv(region),
            "region_type": region_type,
            "zone": join_csv(zone),
            "urgency": join_csv(urgency),
            "severity": join_csv(severity),
            "certainty": join_csv(certainty),
            "limit": limit,
        }
        return self._request(endpoint, params=params)

    def get_active_alerts(
        self,
        start: DateType = None,
        end: DateType = None,
        status: IdType = None,
        message_type: IdType = None,
        event: IdType = None,
        code: IdType = None,
        area: IdType = None,
        point: Optional[str] = None,
        region: IdType = None,
        region_type: Optional[str] = None,
        zone: IdType = None,
        urgency: IdType = None,
        severity: IdType = None,
        certainty: IdType = None,
        limit: Optional[int] = None,
    ) -> dict:
        """Get currently active weather alerts."""
        return self.get_alerts(
            active=True,
            start=start,
            end=end,
            status=status,
            message_type=message_type,
            event=event,
            code=code,
            area=area,
            point=point,
            region=region,
            region_type=region_type,
            zone=zone,
            urgency=urgency,
            severity=severity,
            certainty=certainty,
            limit=limit,
        )

    def get_alert(self, alert_id: str) -> dict:
        """Get a specific alert by ID.

        :param alert_id: Alert identifier string
        :return: Alert feature dictionary
        """
        validate_non_empty_string(alert_id, "alert_id")
        endpoint = f"alerts/{alert_id}"
        return self._request(endpoint)

    def get_active_alerts_count(self) -> dict:
        """Get count of active alerts by zone, area, and region."""
        return self._request("alerts/active/count")

    def get_active_alerts_by_zone(self, zone_id: str) -> dict:
        """Get active alerts for a specific zone (e.g. 'CAZ006')."""
        validate_non_empty_string(zone_id, "zone_id")
        endpoint = f"alerts/active/zone/{zone_id.upper()}"
        return self._request(endpoint)

    def get_active_alerts_by_area(self, area: str) -> dict:
        """Get active alerts for a state or marine area (e.g. 'CA')."""
        validate_non_empty_string(area, "area")
        endpoint = f"alerts/active/area/{area.upper()}"
        return self._request(endpoint)

    # -------------------------------------------------------------------------
    # Stations & Observations Endpoints
    # -------------------------------------------------------------------------

    def get_stations(
        self,
        station_id: Optional[str] = None,
        state: IdType = None,
        limit: Optional[int] = None,
    ) -> dict:
        """Get weather stations or metadata for a single station.

        :param station_id: Station identifier (e.g. 'KJFK'), defaults to None
        :param state: Filter by state/territory code(s) (e.g. 'NY')
        :param limit: Result limit
        :return: Station or station collection dictionary
        """
        if station_id:
            validate_non_empty_string(station_id, "station_id")
            endpoint = f"stations/{station_id.upper()}"
            return self._request(endpoint)

        if limit is not None:
            validate_positive_int(limit, "limit", allow_zero=False)

        params: Dict[str, Any] = {
            "state": join_csv(state),
            "limit": limit,
        }
        return self._request("stations", params=params)

    def get_station_observations(
        self,
        station_id: str,
        start: DateType = None,
        end: DateType = None,
        limit: Optional[int] = None,
    ) -> dict:
        """Get observations for a specific weather station.

        :param station_id: Station identifier (e.g. 'KJFK')
        :param start: Start time
        :param end: End time
        :param limit: Result limit
        :return: Observations collection dictionary
        """
        validate_non_empty_string(station_id, "station_id")
        if limit is not None:
            validate_positive_int(limit, "limit", allow_zero=False)

        parsed_start = parse_date(start, "start", include_time=True)
        parsed_end = parse_date(end, "end", include_time=True)

        params: Dict[str, Any] = {
            "start": parsed_start,
            "end": parsed_end,
            "limit": limit,
        }
        endpoint = f"stations/{station_id.upper()}/observations"
        return self._request(endpoint, params=params)

    def get_latest_observation(
        self,
        station_id: str,
        require_qc: Optional[bool] = None,
    ) -> dict:
        """Get the latest observation for a station.

        :param station_id: Station identifier (e.g. 'KJFK')
        :param require_qc: Require quality-controlled data, defaults to None
        :return: Latest observation dictionary
        """
        validate_non_empty_string(station_id, "station_id")
        params: Dict[str, Any] = {}
        if require_qc is not None:
            validate_boolean(require_qc, "require_qc")
            params["require_qc"] = "true" if require_qc else "false"

        endpoint = f"stations/{station_id.upper()}/observations/latest"
        return self._request(endpoint, params=params)

    # -------------------------------------------------------------------------
    # Zones, Offices & Glossary Endpoints
    # -------------------------------------------------------------------------

    def get_zones(
        self,
        zone_type: Optional[str] = None,
        zone_id: Optional[str] = None,
        area: IdType = None,
        region: IdType = None,
        point: Optional[str] = None,
        include_geometry: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """Get NWS forecast/public/marine zones.

        :param zone_type: Zone type (e.g. 'land', 'forecast', 'marine')
        :param zone_id: Specific zone ID
        :param area: Filter by state or territory code(s)
        :param region: Filter by region
        :param point: Filter by coordinate 'lat,lon'
        :param include_geometry: Include zone geometry GeoJSON
        :param limit: Limit results
        :return: Zones dictionary
        """
        validate_zone_type(zone_type)
        if zone_id:
            validate_non_empty_string(zone_id, "zone_id")
            type_part = zone_type.lower() if zone_type else "forecast"
            endpoint = f"zones/{type_part}/{zone_id.upper()}"
            return self._request(endpoint)

        if limit is not None:
            validate_positive_int(limit, "limit", allow_zero=False)
        if include_geometry is not None:
            validate_boolean(include_geometry, "include_geometry")

        params: Dict[str, Any] = {
            "type": zone_type.lower() if zone_type else None,
            "area": join_csv(area),
            "region": join_csv(region),
            "point": point,
            "include_geometry": (
                "true"
                if include_geometry is True
                else ("false" if include_geometry is False else None)
            ),
            "limit": limit,
        }

        endpoint = f"zones/{zone_type.lower()}" if zone_type else "zones"
        return self._request(endpoint, params=params)

    def get_zone_forecast(self, zone_type: str, zone_id: str) -> dict:
        """Get the forecast for a specific zone.

        :param zone_type: Zone type (e.g. 'forecast', 'public', 'marine')
        :param zone_id: Zone identifier (e.g. 'CAZ006')
        :return: Zone forecast dictionary
        """
        validate_zone_type(zone_type)
        validate_non_empty_string(zone_id, "zone_id")
        endpoint = f"zones/{zone_type.lower()}/{zone_id.upper()}/forecast"
        return self._request(endpoint)

    def get_office(self, office_id: str) -> dict:
        """Get metadata for a Weather Forecast Office (WFO).

        :param office_id: 3-character office code (e.g. 'OKX', 'BOX')
        :return: Office metadata dictionary
        """
        validate_non_empty_string(office_id, "office_id")
        endpoint = f"offices/{office_id.upper()}"
        return self._request(endpoint)

    def get_glossary(self) -> dict:
        """Get NWS glossary terms and definitions."""
        return self._request("glossary")


API = Weather
__all__ = ["Weather", "API"]
