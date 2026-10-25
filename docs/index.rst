NOAA Climate & Weather API Documentation
=========================================

Welcome to the NOAA Python client documentation.
This library provides a convenient interface to access historical climate data
(via Climate Data Online) and current weather forecasts, alerts, and observations
(via the National Weather Service API).

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api
   examples

Features
--------

* Simple, intuitive interface to NOAA CDO and NWS Weather APIs
* Full coverage of CDO (Climate) and NWS (Weather) endpoints
* Comprehensive input validation
* Type hints for better IDE support
* Extensive test coverage
* Well-documented with examples

Installation
------------

Using pip:

.. code-block:: shell

    pip install noaa-climate

Using uv:

.. code-block:: shell

    uv pip install noaa-climate

Quick Examples
--------------

Weather Forecast & Alerts (No token needed):

.. code-block:: python

    from noaa import Weather

    # Initialize weather client
    weather = Weather()

    # Get 7-day forecast for coordinates (New York City)
    forecast = weather.get_forecast(40.7128, -74.0060)

    # Get active weather alerts for California
    alerts = weather.get_active_alerts(area="CA")

Climate Data Online (Token required):

.. code-block:: python

    from noaa import Climate  # or NOAA

    # Initialize client with your API token
    client = Climate("your-api-token-here")

    # Get available datasets
    datasets = client.get_datasets(limit=10)

    # Get temperature data for a location
    data = client.get_data(
        dataset_id="GHCND",
        station_id="GHCND:USW00094728",
        start_date="2023-01-01",
        end_date="2023-01-31",
        data_type_id=["TMAX", "TMIN"]
    )

Getting a Climate API Token
---------------------------

To use the Climate Data Online API (``Climate`` / ``NOAA``), you need an API token:

1. Visit https://www.ncdc.noaa.gov/cdo-web/token
2. Enter your email address
3. You'll receive a token via email (usually within minutes)

Note: The Weather API (``Weather``) does NOT require an API token.

API Overview
------------

**Climate (CDO API)**
    * **Datasets**: Access available climate datasets (GHCND, GSOM, etc.)
    * **Data Categories**: Browse data categories (Temperature, Precipitation, etc.)
    * **Data Types**: Explore specific data types (TMAX, TMIN, PRCP, etc.)
    * **Locations**: Search and filter geographic locations
    * **Stations**: Find climate stations and their metadata
    * **Data**: Retrieve actual climate observations

**Weather (NWS API)**
    * **Points & Forecasts**: Forecasts and gridpoint data by latitude/longitude
    * **Alerts**: Real-time weather watches, warnings, and advisories
    * **Stations & Observations**: Hourly/latest station observations
    * **Zones & Offices**: NWS public/marine zones and Forecast Offices

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`