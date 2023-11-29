# ITMO IDU Database Utilities

This repository contains code and utilities developed for working with the ITMO IDU database.
The codebase includes a variety of scripts and functionalities designed to interact with and manipulate data within the ITMO IDU database.


## Duplicated Services
The Duplicated Services utility is a lightweight script designed to identify and remove duplicated services within buildings,
typically arising from unsuccessful file uploads

The [config.example.json](DuplicatedServices/config.example.json) file describes the configuration file:
- `sqlConnection` - PostgreSQL DSN connection string
- `dry-run` - If true, found services will not be deleted.
- `service_ids` - List of services ids to search duplicated data in 

## Building points
This is a mini-utility for locating and removing building points from database,
as well as transferring city-services from them to neighboring buildings.

The [config.example.json](BuildingPoints/config.example.json) file describes the configuration file:
- `city` - City name
- `from file` - If true, the files buildings_{city}.geojson and services_{city}.geojson should be present in the /data directory, 
the next two parameters is not mandatory to fill in
- `sqlConnection` - PostgreSQL DSN connection string
- `save_data` - If true, buildings and services will be saved in the form they stored in the database to /data
- `distance_limit` - distance in meters, if a building point is located within distance <= distance_limit to another building, they will be merged
- `dry-run` - If true, building points will not be deleted, and services will not be transferred

The [building_fixes_<b>city</b>.log](BuildingPoints/building_fixes_example.log) file describes an example log
