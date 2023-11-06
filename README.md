This is a mini-utility for locating and removing building points from the ITMO IDU database, as well as transferring city-services from them to neighboring points.

The config.example.json file describes the configuration file:

    // City name
    "city": "updated-city-name",
    
    // If True, the files buildings_{city}.geojson and services_{city}.geojson should be present in the working directory, 
    // the next parameter is not mandatory to fill in
    "from_file": false,
    
    // PostgreSQL DSN connection string
    "sqlConnection": "postgresql://user:password@host:5432/db_name",
    
    // distance in meters, if a building point is located within distance <= distance_limit to another building, they will be merged
    "distance_limit": 30,
    
    // If True, building points will not be deleted, and services will not be transferred
    "dry_run": false
