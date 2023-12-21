# ITMO IDU Database Utilities

This repository contains code and utilities developed for working with the ITMO IDU database.
The codebase includes a variety of scripts and functionalities designed to interact with and manipulate data within the ITMO IDU database.


## Duplicated Services
The Duplicated Services utility is a lightweight script designed to identify and remove duplicated services within buildings,
typically arising from unsuccessful file uploads

The [config.example.json](duplicated_services/config.example.json) file describes the configuration file:
- `sqlConnection` - PostgreSQL DSN connection string
- `dry_run` - If true, found services will not be deleted.
- `service_ids` - List of services ids to search duplicated data in 

## Building points
This is a mini-utility for locating and removing building points from database,
as well as transferring city-services from them to neighboring buildings.

The [config.example.json](building_points/config.example.json) file describes the configuration file:
- `city` - City name
- `from file` - If true, the files buildings_{city}.geojson and services_{city}.geojson should be present in the /data directory, 
the next two parameters is not mandatory to fill in
- `sqlConnection` - PostgreSQL DSN connection string
- `save_data` - If true, buildings and services will be saved in the form they stored in the database to /data
- `distance_limit` - distance in meters, if a building point is located within distance <= distance_limit to another building, they will be merged
- `dry_run` - If true, building points will not be deleted, and services will not be transferred

The [building_fixes_<b>city</b>.log](building_points/building_fixes_example.log) file describes an example log

## Admin Municipality
One-time ipynb script created upon IDU's request to swap administrative and municipal units due to the established urban hierarchy in the database.

## Maintenance Update
ipynb script based on the work by [@kanootoko](https://github.com/kanootoko). It is used for updating the maintenance schema in the IDU database. The script operates on a table of a specific format.

## Public transport graph
ipynb script based on the code by [@RitaMargari](https://github.com/RitaMargari), the [data_collecting module of the CityGeoTools package](https://github.com/iduprojects/CityGeoTools/tree/master/data_collecting). My task was to add the ability to load transport routes into the script from a file without making requests to OSMTurbo. Special thanks to [@GeorgeKontsevik](https://github.com/GeorgeKontsevik) for his valuable contributions.