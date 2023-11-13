# Check_buildings

This is a mini-utility for locating and removing building points from the ITMO IDU database,
as well as transferring city-services from them to neighboring buildings.

The [config.example.json](./config.example.json) file describes the configuration file:
- `city` - City name
- `from file` - If true, the files buildings_{city}.geojson and services_{city}.geojson should be present in the /data directory, 
the next two parameters is not mandatory to fill in
- `sqlConnection` - PostgreSQL DSN connection string
- `save_data` - If true, buildings and services will be saved in the form they stored in the database to /data
- `distance_limit` - distance in meters, if a building point is located within distance <= distance_limit to another building, they will be merged
- `dry-run` - If true, building points will not be deleted, and services will not be transferred

The [building_fixes_<b>city</b>.log](./building_fixes_example.log) file describes an example log