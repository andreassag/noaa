"""NOAA Climate Data Online API client."""

import datetime
import urllib.parse
from typing import Optional, Sequence, Union

from noaa.exceptions import ValidationError
from noaa.utils import (
    build_query_params,
    join_ids,
    make_api_request,
    parse_date,
)
from noaa.validators import (
    validate_boolean,
    validate_limit,
    validate_non_empty_string,
    validate_offset,
    validate_sort_field,
    validate_sort_order,
    validate_string_or_none,
    validate_string_or_sequence,
    validate_units,
)

IdType = Optional[Union[str, Sequence[str]]]
DateType = Optional[Union[str, datetime.date, datetime.datetime]]
RequiredDateType = Union[str, datetime.date, datetime.datetime]


class Climate:
    """Client for interfacing with NOAA Climate Data Online API.

    :param token: Access token from NOAA
    :type token: str
    :param timeout: Request timeout in seconds, defaults to 30.0
    :type timeout: float
    """

    BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"

    def __init__(self, token: str, timeout: float = 30.0) -> None:
        if not isinstance(token, str) or not token:
            raise ValidationError("token must be a non-empty string")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise ValidationError("timeout must be a positive number")
        self._headers = {"token": token}
        self.timeout = float(timeout)

    def get_datasets(
        self,
        dataset_id: Optional[str] = None,
        data_type_id: IdType = None,
        location_id: IdType = None,
        station_id: IdType = None,
        start_date: DateType = None,
        end_date: DateType = None,
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
    ) -> dict:
        """Get available datasets or info on a specific dataset.

        :param dataset_id: Dataset identifier, defaults to None
        :param data_type_id: Data type identifier(s), defaults to None
        :param location_id: Location identifier(s), defaults to None
        :param station_id: Station identifier(s), defaults to None
        :param start_date: Start date, defaults to None
        :param end_date: End date, defaults to None
        :param sort_field: Field to sort by, defaults to None
        :param sort_order: Sort order ('asc' or 'desc'), defaults to "asc"
        :param limit: Maximum results (0-1000), defaults to 25
        :param offset: Result offset, defaults to 0
        :return: API response data
        """
        validate_string_or_none(dataset_id, "dataset_id")

        endpoint = "datasets"
        if dataset_id:
            endpoint = f"datasets/{dataset_id}"

        return self._request(
            endpoint=endpoint,
            data_type_id=data_type_id,
            location_id=location_id,
            station_id=station_id,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_data_categories(
        self,
        category_id: Optional[str] = None,
        dataset_id: IdType = None,
        location_id: IdType = None,
        station_id: IdType = None,
        start_date: DateType = None,
        end_date: DateType = None,
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
    ) -> dict:
        """Get available data categories or info on a specific category.

        :param category_id: Category identifier, defaults to None
        :param dataset_id: Dataset identifier(s), defaults to None
        :param location_id: Location identifier(s), defaults to None
        :param station_id: Station identifier(s), defaults to None
        :param start_date: Start date, defaults to None
        :param end_date: End date, defaults to None
        :param sort_field: Field to sort by, defaults to None
        :param sort_order: Sort order ('asc' or 'desc'), defaults to "asc"
        :param limit: Maximum results (0-1000), defaults to 25
        :param offset: Result offset, defaults to 0
        :return: API response data
        """
        validate_string_or_none(category_id, "category_id")

        endpoint = "datacategories"
        if category_id:
            endpoint = f"datacategories/{category_id}"

        return self._request(
            endpoint=endpoint,
            dataset_id=dataset_id,
            location_id=location_id,
            station_id=station_id,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_data_types(
        self,
        type_id: Optional[str] = None,
        dataset_id: IdType = None,
        location_id: IdType = None,
        station_id: IdType = None,
        data_category_id: IdType = None,
        start_date: DateType = None,
        end_date: DateType = None,
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
    ) -> dict:
        """Get available data types or info on a specific type.

        :param type_id: Type identifier, defaults to None
        :param dataset_id: Dataset identifier(s), defaults to None
        :param location_id: Location identifier(s), defaults to None
        :param station_id: Station identifier(s), defaults to None
        :param data_category_id: Data category identifier(s), defaults to None
        :param start_date: Start date, defaults to None
        :param end_date: End date, defaults to None
        :param sort_field: Field to sort by, defaults to None
        :param sort_order: Sort order ('asc' or 'desc'), defaults to "asc"
        :param limit: Maximum results (0-1000), defaults to 25
        :param offset: Result offset, defaults to 0
        :return: API response data
        """
        validate_string_or_none(type_id, "type_id")

        endpoint = "datatypes"
        if type_id:
            endpoint = f"datatypes/{type_id}"

        return self._request(
            endpoint=endpoint,
            dataset_id=dataset_id,
            location_id=location_id,
            station_id=station_id,
            data_category_id=data_category_id,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_location_categories(
        self,
        location_category_id: Optional[str] = None,
        dataset_id: IdType = None,
        start_date: DateType = None,
        end_date: DateType = None,
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
    ) -> dict:
        """Get available location categories or info on a specific category.

        :param location_category_id: Location category id, defaults to None
        :param dataset_id: Dataset identifier(s), defaults to None
        :param start_date: Start date, defaults to None
        :param end_date: End date, defaults to None
        :param sort_field: Field to sort by, defaults to None
        :param sort_order: Sort order ('asc' or 'desc'), defaults to "asc"
        :param limit: Maximum results (0-1000), defaults to 25
        :param offset: Result offset, defaults to 0
        :return: API response data
        """
        validate_string_or_none(location_category_id, "location_category_id")

        endpoint = "locationcategories"
        if location_category_id:
            endpoint = f"locationcategories/{location_category_id}"

        return self._request(
            endpoint=endpoint,
            dataset_id=dataset_id,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_locations(
        self,
        location_id: Optional[str] = None,
        dataset_id: IdType = None,
        location_category_id: IdType = None,
        data_category_id: IdType = None,
        start_date: DateType = None,
        end_date: DateType = None,
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
    ) -> dict:
        """Get available locations or info on a specific location.

        :param location_id: Location identifier, defaults to None
        :param dataset_id: Dataset identifier(s), defaults to None
        :param location_category_id: Location category identifier(s)
        :param data_category_id: Data category identifier(s)
        :param start_date: Start date, defaults to None
        :param end_date: End date, defaults to None
        :param sort_field: Field to sort by, defaults to None
        :param sort_order: Sort order ('asc' or 'desc'), defaults to "asc"
        :param limit: Maximum results (0-1000), defaults to 25
        :param offset: Result offset, defaults to 0
        :return: API response data
        """
        validate_string_or_none(location_id, "location_id")

        endpoint = "locations"
        if location_id:
            endpoint = f"locations/{location_id}"

        return self._request(
            endpoint=endpoint,
            dataset_id=dataset_id,
            location_category_id=location_category_id,
            data_category_id=data_category_id,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_stations(
        self,
        station_id: Optional[str] = None,
        dataset_id: IdType = None,
        location_id: IdType = None,
        data_category_id: IdType = None,
        data_type_id: IdType = None,
        extent: Optional[str] = None,
        start_date: DateType = None,
        end_date: DateType = None,
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
    ) -> dict:
        """Get available stations or info on a specific station.

        :param station_id: Station identifier, defaults to None
        :param dataset_id: Dataset identifier(s), defaults to None
        :param location_id: Location identifier(s), defaults to None
        :param data_category_id: Data category identifier(s)
        :param data_type_id: Data type identifier(s)
        :param extent: Geographic extent for search, defaults to None
        :param start_date: Start date, defaults to None
        :param end_date: End date, defaults to None
        :param sort_field: Field to sort by, defaults to None
        :param sort_order: Sort order ('asc' or 'desc'), defaults to "asc"
        :param limit: Maximum results (0-1000), defaults to 25
        :param offset: Result offset, defaults to 0
        :return: API response data
        """
        validate_string_or_none(station_id, "station_id")

        endpoint = "stations"
        if station_id:
            endpoint = f"stations/{station_id}"

        return self._request(
            endpoint=endpoint,
            dataset_id=dataset_id,
            location_id=location_id,
            data_category_id=data_category_id,
            data_type_id=data_type_id,
            extent=extent,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_data(
        self,
        dataset_id: str,
        start_date: RequiredDateType,
        end_date: RequiredDateType,
        data_type_id: IdType = None,
        location_id: IdType = None,
        station_id: IdType = None,
        units: str = "metric",
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
        include_metadata: bool = False,
    ) -> dict:
        """Get climate data from CDO.

        :param dataset_id: Dataset identifier (required)
        :param start_date: Start date in ISO format or date object (required)
        :param end_date: End date in ISO format or date object (required)
        :param data_type_id: Data type identifier(s), defaults to None
        :param location_id: Location identifier(s), defaults to None
        :param station_id: Station identifier(s), defaults to None
        :param units: Units ('metric' or 'standard'), defaults to "metric"
        :param sort_field: Field to sort by, defaults to None
        :param sort_order: Sort order ('asc' or 'desc'), defaults to "asc"
        :param limit: Maximum results (0-1000), defaults to 25
        :param offset: Result offset, defaults to 0
        :param include_metadata: Include metadata in response
        :return: API response data
        """
        validate_non_empty_string(dataset_id, "dataset_id")
        if start_date is None:
            raise ValidationError("start_date must be provided")
        if end_date is None:
            raise ValidationError("end_date must be provided")

        return self._request(
            endpoint="data",
            dataset_id=dataset_id,
            data_type_id=data_type_id,
            location_id=location_id,
            station_id=station_id,
            start_date=start_date,
            end_date=end_date,
            units=units,
            sort_field=sort_field,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            include_metadata=include_metadata,
            include_time=True,
        )

    def _request(
        self,
        endpoint: str,
        dataset_id: IdType = None,
        data_type_id: IdType = None,
        data_category_id: IdType = None,
        location_id: IdType = None,
        location_category_id: IdType = None,
        station_id: IdType = None,
        start_date: DateType = None,
        end_date: DateType = None,
        extent: Optional[str] = None,
        units: str = "metric",
        sort_field: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 25,
        offset: int = 0,
        include_metadata: bool = False,
        include_time: bool = False,
    ) -> dict:
        """Make a request to the NOAA API."""
        # Validate all ID parameters
        for name, value in [
            ("dataset_id", dataset_id),
            ("data_type_id", data_type_id),
            ("data_category_id", data_category_id),
            ("location_id", location_id),
            ("location_category_id", location_category_id),
            ("station_id", station_id),
        ]:
            validate_string_or_sequence(value, name)

        validate_string_or_none(extent, "extent")
        validate_limit(limit)
        validate_offset(offset)
        validate_sort_field(sort_field)
        validate_sort_order(sort_order)
        validate_units(units)
        validate_boolean(include_metadata, "include_metadata")

        # Parse dates
        parsed_start = parse_date(start_date, "start_date", include_time)
        parsed_end = parse_date(end_date, "end_date", include_time)

        # Build parameters
        params = {
            "datasetid": join_ids(dataset_id),
            "datatypeid": join_ids(data_type_id),
            "datacategoryid": join_ids(data_category_id),
            "locationid": join_ids(location_id),
            "locationcategoryid": join_ids(location_category_id),
            "stationid": join_ids(station_id),
            "startdate": parsed_start,
            "enddate": parsed_end,
            "extent": extent,
            "units": units,
            "sortfield": sort_field,
            "sortorder": sort_order,
            "limit": limit,
            "offset": offset,
            "includemetadata": include_metadata if include_metadata else None,
        }

        query_string = build_query_params(params)
        url = urllib.parse.urljoin(self.BASE_URL, endpoint)
        full_url = f"{url}?{query_string}" if query_string else url

        return make_api_request(full_url, self._headers, timeout=self.timeout)


NOAA = Climate
