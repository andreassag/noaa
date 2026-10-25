Examples
========

This page contains practical examples of using the NOAA Climate API client.

Example 1: Temperature Analysis
--------------------------------

Get daily high and low temperatures for a location:

.. code-block:: python

    from noaa import NOAA
    from datetime import datetime, timedelta

    client = NOAA("your-api-token")

    # Get data for the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    data = client.get_data(
        dataset_id="GHCND",
        station_id="GHCND:USW00094728",  # Central Park, NYC
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        data_type_id=["TMAX", "TMIN"],
        units="metric"
    )

    # Process the data
    temps = {}
    for record in data['results']:
        date = record['date'][:10]
        if date not in temps:
            temps[date] = {}
        temps[date][record['datatype']] = record['value'] / 10  # Convert to Celsius

    # Print results
    for date in sorted(temps.keys()):
        if 'TMAX' in temps[date] and 'TMIN' in temps[date]:
            print(f"{date}: High {temps[date]['TMAX']}°C, Low {temps[date]['TMIN']}°C")

Example 2: Precipitation Data
------------------------------

Get precipitation data for multiple stations:

.. code-block:: python

    from noaa import NOAA

    client = NOAA("your-api-token")

    # Find stations in a state
    stations = client.get_stations(
        dataset_id="GHCND",
        location_id="FIPS:06",  # California
        data_type_id="PRCP",
        limit=10
    )

    station_ids = [s['id'] for s in stations['results']]

    # Get precipitation data
    data = client.get_data(
        dataset_id="GHCND",
        station_id=station_ids,
        start_date="2023-01-01",
        end_date="2023-12-31",
        data_type_id="PRCP",
        units="metric"
    )

    # Calculate total precipitation per station
    precip_by_station = {}
    for record in data['results']:
        station = record['station']
        value = record['value'] / 10  # Convert to mm
        precip_by_station[station] = precip_by_station.get(station, 0) + value

    for station, total in precip_by_station.items():
        print(f"{station}: {total:.1f} mm")

Example 3: Geographic Search
-----------------------------

Find weather stations within a bounding box:

.. code-block:: python

    from noaa import NOAA

    client = NOAA("your-api-token")

    # Define bounding box for San Francisco Bay Area
    # Format: minLat, minLon, maxLat, maxLon
    extent = "37.0,-123.0,38.5,-121.5"

    stations = client.get_stations(
        dataset_id="GHCND",
        extent=extent,
        limit=50
    )

    print(f"Found {len(stations['results'])} stations:")
    for station in stations['results']:
        print(f"  {station['name']}")
        print(f"    Location: {station['latitude']}, {station['longitude']}")
        print(f"    Elevation: {station['elevation']} m")
        print(f"    Data coverage: {station['datacoverage']}")
        print()

Example 4: Data Type Discovery
-------------------------------

Find available data types for a dataset:

.. code-block:: python

    from noaa import NOAA

    client = NOAA("your-api-token")

    # Get all data types for GHCND dataset
    data_types = client.get_data_types(
        dataset_id="GHCND",
        limit=100
    )

    # Filter for temperature-related types
    temp_types = [
        dt for dt in data_types['results']
        if 'temp' in dt['name'].lower()
    ]

    print("Temperature data types:")
    for dt in temp_types:
        print(f"  {dt['id']}: {dt['name']}")

Example 5: Pagination Through Large Results
--------------------------------------------

Retrieve all stations for a dataset using pagination:

.. code-block:: python

    from noaa import NOAA

    client = NOAA("your-api-token")

    all_stations = []
    offset = 0
    limit = 1000

    while True:
        response = client.get_stations(
            dataset_id="GHCND",
            location_id="FIPS:37",  # North Carolina
            limit=limit,
            offset=offset
        )
        
        stations = response['results']
        all_stations.extend(stations)
        
        # Check if we got all results
        metadata = response.get('metadata', {}).get('resultset', {})
        count = metadata.get('count', 0)
        
        if len(all_stations) >= count:
            break
            
        offset += limit

    print(f"Retrieved {len(all_stations)} total stations")

Example 6: Date Range with Datetime Objects
--------------------------------------------

Use datetime objects for date parameters:

.. code-block:: python

    from noaa import NOAA
    from datetime import datetime, timedelta

    client = NOAA("your-api-token")

    # Define date range
    end = datetime.now()
    start = end - timedelta(days=7)  # Last 7 days

    data = client.get_data(
        dataset_id="GHCND",
        station_id="GHCND:USW00094728",
        start_date=start,  # Pass datetime object
        end_date=end,      # Pass datetime object
        data_type_id="TMAX"
    )

Example 7: Export to CSV
-------------------------

Export climate data to a CSV file:

.. code-block:: python

    from noaa import NOAA
    import csv

    client = NOAA("your-api-token")

    data = client.get_data(
        dataset_id="GHCND",
        station_id="GHCND:USW00094728",
        start_date="2023-01-01",
        end_date="2023-12-31",
        data_type_id=["TMAX", "TMIN", "PRCP"],
        limit=1000
    )

    # Write to CSV
    with open('climate_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['date', 'station', 'datatype', 'value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in data['results']:
            writer.writerow({
                'date': record['date'],
                'station': record['station'],
                'datatype': record['datatype'],
                'value': record['value']
            })

    print("Data exported to climate_data.csv")

Example 8: Working with Location Categories
--------------------------------------------

Explore different types of locations:

.. code-block:: python

    from noaa import NOAA

    client = NOAA("your-api-token")

    # Get all location categories
    categories = client.get_location_categories()
    
    print("Available location categories:")
    for cat in categories['results']:
        print(f"  {cat['id']}: {cat['name']}")
    
    # Get locations for a specific category
    states = client.get_locations(
        location_category_id="ST",
        limit=50
    )
    
    print("\nStates:")
    for state in states['results']:
        print(f"  {state['name']}: {state['id']}")

Example 9: Monthly Summaries
-----------------------------

Get monthly summary data:

.. code-block:: python

    from noaa import NOAA

    client = NOAA("your-api-token")

    # Get monthly data (GSOM dataset)
    data = client.get_data(
        dataset_id="GSOM",
        station_id="GHCND:USW00094728",
        start_date="2023-01-01",
        end_date="2023-12-31",
        data_type_id=["TAVG", "PRCP"]
    )

    print("Monthly summaries:")
    for record in data['results']:
        date = record['date']
        dtype = record['datatype']
        value = record['value']
        
        if dtype == "TAVG":
            print(f"{date}: Avg Temp = {value/10}°C")
        elif dtype == "PRCP":
            print(f"{date}: Total Precip = {value/10}mm")

Example 10: Comparing Multiple Locations
-----------------------------------------

Compare climate data across different locations:

.. code-block:: python

    from noaa import NOAA
    from collections import defaultdict

    client = NOAA("your-api-token")

    # Define stations to compare
    stations = {
        "New York": "GHCND:USW00094728",
        "Los Angeles": "GHCND:USW00023174",
        "Chicago": "GHCND:USW00094846"
    }

    # Get data for all stations
    data = client.get_data(
        dataset_id="GHCND",
        station_id=list(stations.values()),
        start_date="2023-07-01",
        end_date="2023-07-31",
        data_type_id="TMAX"
    )

    # Calculate average max temperature per station
    temps = defaultdict(list)
    for record in data['results']:
        station_id = record['station']
        temps[station_id].append(record['value'] / 10)

    # Print results
    print("Average July Maximum Temperature:")
    station_lookup = {v: k for k, v in stations.items()}
    for station_id, values in temps.items():
        city = station_lookup.get(station_id, station_id)
        avg_temp = sum(values) / len(values)
        print(f"  {city}: {avg_temp:.1f}°C")


Example 10: Real-Time Weather Forecast & Hourly Breakdown
---------------------------------------------------------

Retrieve the 7-day forecast and hourly forecast using coordinates (NWS Weather API):

.. code-block:: python

    from noaa import Weather

    weather = Weather()

    # Coordinates for Seattle, WA
    lat, lon = 47.6062, -122.3321

    # 7-day textual forecast
    forecast = weather.get_forecast(lat, lon)
    for period in forecast['properties']['periods'][:5]:
        print(f"{period['name']}: {period['temperature']}°{period['temperatureUnit']} - {period['detailedForecast']}")

    # Hourly forecast
    hourly = weather.get_forecast(lat, lon, hourly=True)
    for hour in hourly['properties']['periods'][:6]:
        print(f"{hour['startTime'][11:16]}: {hour['temperature']}°{hour['temperatureUnit']} ({hour['shortForecast']})")

Example 11: Real-Time Weather Alerts Tracking
---------------------------------------------

Monitor active weather warnings, watches, and advisories:

.. code-block:: python

    from noaa import Weather

    weather = Weather()

    # Active alerts in Florida
    alerts = weather.get_active_alerts(area="FL")
    print(f"Total active alerts in Florida: {len(alerts['features'])}")

    for feature in alerts['features']:
        props = feature['properties']
        print(f"[{props['severity'].upper()}] {props['event']}: {props['headline']}")
