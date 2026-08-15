# NOAA Climate Data Online API Client

A Python client for accessing the NOAA Climate Data Online (CDO) API. This library provides a simple, intuitive interface to retrieve historical weather and climate data from NOAA's extensive archive.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- Simple, intuitive interface to NOAA CDO API
- Full coverage of all CDO endpoints (datasets, stations, locations, data)
- Comprehensive input validation with helpful error messages
- Type hints for better IDE support
- Extensive test coverage (80%+)
- Well-documented with examples

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

### Get an API Token

1. Visit https://www.ncdc.noaa.gov/cdo-web/token
2. Enter your email address
3. Receive your token via email (usually within minutes)

### Basic Usage

```python
from noaa import NOAA

# Initialize client
client = NOAA("your-api-token-here")

# Get available datasets
datasets = client.get_datasets(limit=10)

# Get temperature data
data = client.get_data(
    dataset_id="GHCND",
    station_id="GHCND:USW00094728",  # Central Park, NYC
    start_date="2023-01-01",
    end_date="2023-01-31",
    data_type_id=["TMAX", "TMIN"]
)
```

## Examples

### Find Stations in a Location

```python
# Find stations in North Carolina
stations = client.get_stations(
    dataset_id="GHCND",
    location_id="FIPS:37",
    limit=10
)

for station in stations['results']:
    print(f"{station['name']}: {station['id']}")
```

### Get Precipitation Data

```python
# Get precipitation for multiple stations
data = client.get_data(
    dataset_id="GHCND",
    station_id=["GHCND:USW00094728", "GHCND:USW00013722"],
    start_date="2023-01-01",
    end_date="2023-12-31",
    data_type_id="PRCP",
    units="metric"
)
```

### Geographic Search

```python
# Find stations within a bounding box (San Francisco Bay Area)
stations = client.get_stations(
    extent="37.0,-123.0,38.5,-121.5",
    dataset_id="GHCND",
    limit=50
)
```

## API Methods

### Datasets
- `get_datasets()` - Get available datasets

### Data Categories
- `get_data_categories()` - Get data category information

### Data Types
- `get_data_types()` - Get available data types (TMAX, TMIN, PRCP, etc.)

### Locations
- `get_location_categories()` - Get location category types
- `get_locations()` - Get location information

### Stations
- `get_stations()` - Find weather stations

### Data
- `get_data()` - Retrieve climate data

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/noaa.git
cd noaa

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
make test

# Run with coverage
make coverage

# Generate HTML coverage report
make coverage-html
```

### Building Documentation

```bash
# Build documentation
make docs

# Serve documentation locally at http://localhost:8000
make docs-serve

# Clean documentation build
make docs-clean
```

## Project Structure

```
noaa/
├── noaa/
│   ├── __init__.py
│   ├── client.py         # Main API client
│   ├── exceptions.py     # Custom exceptions
│   ├── validators.py     # Input validation
│   ├── utils.py          # Utility functions
│   └── climate.py        # Backwards compatibility
├── tests/
│   ├── test_client.py
│   ├── test_validators.py
│   ├── test_utils.py
│   └── conftest.py
├── docs/
│   ├── conf.py
│   ├── index.rst
│   └── ...
└── pyproject.toml
```

## Documentation

Full documentation is available at https://andreassag.github.io/noaa/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [NOAA CDO API Documentation](https://www.ncdc.noaa.gov/cdo-web/webservices/v2)
- [Request API Token](https://www.ncdc.noaa.gov/cdo-web/token)
- [NOAA CDO Web Interface](https://www.ncdc.noaa.gov/cdo-web/)

## Support

- Report issues on [GitHub Issues](https://github.com/yourusername/noaa/issues)
- Read the [documentation](docs/)
- Ask questions in [Discussions](https://github.com/yourusername/noaa/discussions)
