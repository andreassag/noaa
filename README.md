> [!IMPORTANT]
> **Archival Notice**
> This repository is archived and is no longer actively maintained. Release `v1.0.0` represents the final, stable version of this library featuring both NOAA Climate Data Online (`Climate` / `NOAA`) and National Weather Service (`Weather`) clients. You are welcome to fork the project for further development.

# NOAA API Client

A modern Python client for NOAA's **Climate Data Online (CDO)** and **National Weather Service (NWS)** APIs. This library provides a clean, unified interface to retrieve historical climate archives as well as live weather forecasts, alerts, and observations.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **National Weather Service API (`Weather`)**:
  - Point metadata, 7-day textual forecasts, and hourly forecasts by latitude/longitude
  - Active and historical weather watches, warnings, and advisories (filtered by state, zone, urgency, severity)
  - Live and historical station observations across airport and marine stations
  - Forecast zones, public zones, Weather Forecast Offices (WFO), and glossary
  - No API key required (requires a user agent)
- **Climate Data Online API (`Climate` / `NOAA`)**:
  - Full coverage of CDO endpoints (datasets, data types, locations, stations, data)
  - Historical observations from GHCND, GSOM, GSOY, and more
  - Filter by date range, station, location category, and units
  - Requires a free CDO API token
- **Reliable & Production-Ready**:
  - Comprehensive input validation with clear errors
  - Configurable timeouts and structured error handling (`APIError`, `ValidationError`)
  - Full typing support for IDE autocomplete
  - Extensive test coverage (90%+)

## Installation

Using pip:

```bash
pip install noaa-climate
```

Using uv:

```bash
uv pip install noaa-climate
```

## Quick Start

### 1. Weather Forecasts & Alerts (`Weather`)

The National Weather Service API (`https://api.weather.gov/`) is public and free to use without an API token:

```python
from noaa import Weather

# Initialize weather client (custom User-Agent recommended)
weather = Weather(user_agent="my-weather-app (contact@example.com)")

# 1. Get 7-day forecast by coordinates (e.g. Central Park, NYC)
forecast = weather.get_forecast(40.7829, -73.9654)
for period in forecast["properties"]["periods"][:3]:
    print(f"{period['name']}: {period['temperature']}°{period['temperatureUnit']} - {period['shortForecast']}")

# 2. Get hourly forecast
hourly = weather.get_forecast(40.7829, -73.9654, hourly=True)
next_hour = hourly["properties"]["periods"][0]
print(f"Next hour: {next_hour['temperature']}°{next_hour['temperatureUnit']}, {next_hour['shortForecast']}")

# 3. Get active weather alerts in a state
alerts = weather.get_active_alerts(area="CA")
print(f"Active alerts in CA: {len(alerts['features'])}")

# 4. Get latest observation from an airport station
obs = weather.get_latest_observation("KJFK")
temp_c = obs["properties"]["temperature"]["value"]
print(f"KJFK Temperature: {temp_c}°C")
```

### 2. Climate Data Online (`Climate` / `NOAA`)

The CDO API requires a free API token:
1. Visit https://www.ncdc.noaa.gov/cdo-web/token
2. Enter your email address to receive your token

```python
from noaa import Climate  # or `from noaa import NOAA`

# Initialize client
client = Climate("your-api-token-here")

# Get available datasets
datasets = client.get_datasets(limit=10)

# Get temperature data
data = client.get_data(
    dataset_id="GHCND",
    station_id="GHCND:USW00094728",  # Central Park, NYC
    start_date="2023-01-01",
    end_date="2023-01-31",
    data_type_id=["TMAX", "TMIN"],
    units="metric",
)
```

## Examples

### Weather Alerts by Severity

```python
from noaa import Weather

weather = Weather()

# Get severe or extreme active alerts
alerts = weather.get_active_alerts(
    severity="severe",
    area="TX",
)
for feature in alerts["features"]:
    props = feature["properties"]
    print(f"[{props['event']}] {props['headline']}")
```

### Station Search & Metadata

```python
from noaa import Weather

weather = Weather()

# Get stations in New York state
stations = weather.get_stations(state="NY", limit=5)
for feature in stations["features"]:
    props = feature["properties"]
    print(f"{props['stationIdentifier']}: {props['name']}")
```

### Error Handling

```python
from noaa import Climate, Weather
from noaa.exceptions import APIError, ValidationError

weather = Weather()

try:
    # Coordinates must be valid latitudes [-90, 90] and longitudes [-180, 180]
    weather.get_forecast(100.0, -74.0)
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API request failed (status {e.status_code}): {e}")
```

## Project Structure

```
noaa/
├── src/noaa/
│   ├── __init__.py       # Package exports (Climate, Weather, NOAA, etc.)
│   ├── client.py         # Climate / NOAA client (CDO API)
│   ├── weather.py        # Weather client (NWS API)
│   ├── exceptions.py     # Custom exceptions (APIError, ValidationError)
│   ├── validators.py     # Input validators
│   ├── utils.py          # HTTP requests and parameter utilities
│   └── climate.py        # Backwards compatibility module
├── tests/
│   ├── test_client.py
│   ├── test_weather.py
│   ├── test_validators.py
│   ├── test_utils.py
│   ├── test_exceptions.py
│   ├── test_climate.py
│   └── conftest.py
├── docs/
└── pyproject.toml
```

## Documentation

Full documentation is available at https://andreassag.github.io/noaa/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [National Weather Service API Documentation](https://www.weather.gov/documentation/services-web-api)
- [NOAA CDO API Documentation](https://www.ncdc.noaa.gov/cdo-web/webservices/v2)
- [Request CDO API Token](https://www.ncdc.noaa.gov/cdo-web/token)

## Support & Contributing

- Report issues on [GitHub Issues](https://github.com/andreassag/noaa/issues)
- Read the [documentation](docs/)
- Ask questions in [Discussions](https://github.com/andreassag/noaa/discussions)
