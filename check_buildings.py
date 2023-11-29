import json
import logging
import os
from datetime import datetime
import geopandas as gpd
import pandas as pd
import sqlalchemy as sa
from sklearn.neighbors import NearestNeighbors

import mapping


def download_buildings(city_name: str, sql_alchemy_engine: sa.Engine, save: bool):
    logging.info(f"Downloading {city_name}'s building")
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text("SELECT id FROM cities WHERE name =:name").params(name=city_name)
        ).scalar_one()
        sql_ = f"SELECT p.geometry, b.* FROM buildings b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
        gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
        if save:
            gdf.to_file(f"data/buildings_{city_name}.geojson")
    logging.info("Done downloading building!\n")
    return gdf


def download_services(city_name: str, sql_alchemy_engine: sa.Engine, save: bool):
    logging.info(f"Downloading {city_name}'s services")
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text("SELECT id FROM cities WHERE name =:name").params(name=city_name)
        ).scalar_one()
        sql_ = f"SELECT p.geometry, b.* FROM functional_objects b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
        gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
        if save:
            gdf.to_file(f"data/services_{city_name}.geojson")
    logging.info("Done downloading services!\n")
    return gdf


def search_neighbor_from_point_buffer(
    points_data: gpd.GeoDataFrame, search_in_data: gpd.GeoDataFrame, radius
) -> gpd.GeoDataFrame:
    search_in_data = search_in_data.to_crs("EPSG:3857")
    points_data = points_data.to_crs("EPSG:3857")
    logging.info("Searching for building-point's neighbors")
    join = gpd.sjoin_nearest(
        points_data,
        search_in_data,
        how="inner",
        max_distance=radius,
        distance_col="dist",
    )
    points_data["closest_building_physical_id"] = join["physical_object_id_right"]
    logging.info("Done searching neighbors!\n")
    return points_data


def upload_services_db(sql_alchemy_engine: sa.Engine, data: gpd.GeoDataFrame):
    logging.info(f"Updating services in DB")
    with sql_alchemy_engine.connect() as connection:
        for ind, row in data.iterrows():
            id_value = row["id"]
            new_physical_object_id = row["physical_object_id"]

            stmt = (
                sa.update(mapping.FunctionalObject)
                .where(mapping.FunctionalObject.id == id_value)
                .values(
                    physical_object_id=new_physical_object_id, updated_at=datetime.now()
                )
            )
            connection.execute(stmt)
        connection.commit()
    logging.info("Done updating!\n")


def remove_building_db(sql_alchemy_engine: sa.Engine, data: gpd.GeoDataFrame):
    logging.info(f"Removing redundant building-points in DB")
    with sql_alchemy_engine.connect() as connection:
        for _, row in data.iterrows():
            building_id = row["id"]
            physical_object_id = row["physical_object_id"]
            stmt = sa.delete(mapping.Building).where(mapping.Building.id == building_id)
            connection.execute(stmt)

            stmt = sa.delete(mapping.PhysicalObject).where(
                mapping.PhysicalObject.id == physical_object_id
            )
            connection.execute(stmt)
        connection.commit()
    logging.info("Done removing!\n")


def main():
    with open(os.path.join(os.getcwd(), "config.json"), encoding="UTF-8") as f:
        config_imputation = json.load(f)
        city = config_imputation["city"]
        sql_connection = config_imputation["sqlConnection"]
        distance_limit = config_imputation["distance_limit"]
        dry_run = config_imputation["dry_run"]
        from_file = config_imputation["from_file"]
        save_data = config_imputation["save_data"]

    log_file_name = f"building_fixes_{city}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(
                os.path.join(os.getcwd(), log_file_name), mode="w", encoding="UTF-8"
            ),
            logging.StreamHandler(),
        ],
    )

    engine = sa.create_engine(sql_connection)
    gdf_services: gpd.GeoDataFrame
    gdf_buildings: gpd.GeoDataFrame
    if not from_file:
        gdf_buildings = download_buildings(city, engine, save_data)
        gdf_services = download_services(city, engine, save_data)
    else:
        logging.info(f"Reading {city}'s services file")
        gdf_services = gpd.read_file(f"data/services_{city}.geojson")
        logging.info(f"Done reading services!\n")

        logging.info(f"Reading {city}'s building file")
        gdf_buildings = gpd.read_file(f"data/buildings_{city}.geojson")
        logging.info(f"Done reading buildings!\n")

    # Выбрать строки, у которых геометрия типа Точка и полигон
    gdf_geom_points = gdf_buildings[(gdf_buildings.geometry.type == "Point")].copy()
    gdf_geom_polygons = gdf_buildings[
        (gdf_buildings.geometry.type in ("Polygon", "MultiPolygon"))
    ].copy()
    if gdf_geom_points.shape[0] == 0:
        logging.info(f"No buildings-points in {city} city, exiting.")
        exit()
    else:
        logging.info(
            f"There are {gdf_geom_points.shape[0]} buildings-point(s) in {city} city."
        )
    gdf_geom_points = search_neighbor_from_point_buffer(
        gdf_geom_points, gdf_geom_polygons, distance_limit
    )  # добавлен столбец с ближайшим соседом не точкой

    # Проверяем на наличие точек-зданий без соседей
    if (
        gdf_geom_points.loc[
            gdf_geom_points["closest_building_physical_id"].isnull()
        ].shape[0]
        > 0
    ):
        gdf_: gpd.GeoDataFrame = (
            gdf_geom_points.loc[
                gdf_geom_points["closest_building_physical_id"].isnull()
            ]
            .filter(["id", "physical_object_id"])
            .reset_index(drop=True)
        )
        gdf_.to_json(f"no_neighbors_{city}.json", orient="records")
        logging.warning(
            f"There are {gdf_.shape[0]} building-point(s) in {city} city with no neighbor in distance = {distance_limit}, check "
            f"<no_neighbors_{city}.json> file"
        )
    points_amount = gdf_geom_points.shape[0]
    # Находим точки, которые надо удалить из бд
    gdf_geom_points = gdf_geom_points.dropna(subset=["closest_building_physical_id"])

    if points_amount == 0:
        logging.info(
            f"No buildings-points in {city} city to remove, services will not be transferred, exiting."
        )
        exit()
    # отделяем сервисы, привязанные к зданиям точкам
    list_buildings_points = gdf_geom_points["physical_object_id"].tolist()
    gdf_services = gdf_services.query("physical_object_id in @list_buildings_points")

    for index, row in gdf_services.iterrows():
        physical_object_id = row["physical_object_id"]
        closest_building_physical_id = (
            gdf_geom_points[
                gdf_geom_points["physical_object_id"] == physical_object_id
            ]["closest_building_physical_id"]
            .explode()
            .unique()
        )

        if len(closest_building_physical_id) > 0:
            gdf_services.loc[
                index, "physical_object_id"
            ] = closest_building_physical_id[0]

    gdf_services = gdf_services.astype({"physical_object_id": int})

    points_amount_to_change = gdf_services.shape[0]
    if points_amount_to_change > 0:
        logging.info(
            f'In the city of "{city}", neighbors were found at a distance of {distance_limit} for {points_amount_to_change} services out of {points_amount} building points.'
        )
        if not dry_run:
            upload_services_db(engine, gdf_services)
            remove_building_db(engine, gdf_geom_points)
        else:
            logging.info("The config specifies a dry run, data will not be saved.")
    else:
        logging.info(f"No services to transfer and no building-points to delete.")


#
# Различные способы найти дистанцию в геометрии
# print((gdf_geom_Polygons.loc[gdf_geom_Polygons["id"] == gdf_geom_Points.iloc[0]['closest_building_id']]).geometry.boundary)
# print(gdf_geom_Points.iloc[0].geometry.distance((gdf_geom_Polygons.loc[gdf_geom_Polygons["id"] == gdf_geom_Points.iloc[0]['closest_building_id']]).geometry))
# geom1 = geopandas.GeoSeries(gdf_geom_Points.iloc[0].geometry)
# geom1.crs = 'EPSG:3857'
# geom2 = geopandas.GeoSeries((gdf_geom_Polygons.loc[gdf_geom_Polygons["id"] == gdf_geom_Points.iloc[0]['closest_building_id']]).geometry)
# geom2.crs = 'EPSG:3857'
# # print(geom2.distance(geom1,align=False))
# print(geom2.exterior.sindex.nearest(geom1,return_distance = True))
# geom3 = geom2.geometry.centroid
# print(geom3.sindex.nearest(geom1,return_distance = True))


if __name__ == "__main__":
    main()


def search_neighbors_from_point(
    points_data: gpd.GeoDataFrame, search_in_data: gpd.GeoDataFrame, n_neigh, radius
) -> gpd.GeoDataFrame:
    x = points_data.to_crs("EPSG:3857").geometry.centroid.apply(lambda point: point.x)
    y = points_data.to_crs("EPSG:3857").geometry.centroid.apply(lambda point: point.y)
    points = pd.DataFrame({"x": x, "y": y})
    x2 = search_in_data.to_crs("EPSG:3857").geometry.centroid.apply(
        lambda point: point.x
    )
    y2 = search_in_data.to_crs("EPSG:3857").geometry.centroid.apply(
        lambda point: point.y
    )
    buildings_points = pd.DataFrame({"x": x2, "y": y2})
    neigh = NearestNeighbors(n_neighbors=n_neigh, radius=radius)
    neigh.fit(buildings_points)
    neigh_dist, neigh_ind = neigh.kneighbors(points)
    neigh_ind = pd.Series(neigh_ind.tolist())

    # print((search_in_data.iloc[neigh_ind.explode()])["id"].explode().reset_index(drop=True))
    index = points_data.index
    points_data = points_data.reset_index(drop=True)
    points_data["closest_building_id"] = (
        (search_in_data.iloc[neigh_ind.explode()])["physical_object_id"]
        .explode()
        .reset_index(drop=True)
    )
    points_data = points_data.set_index(index)

    # rows_to_keep = neigh_ind.explode().unique()
    # search_in_data_filtered = search_in_data.iloc[rows_to_keep]

    return points_data


def save_city_to_file(city_name: str, sql_alchemy_engine: sa.Engine):
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text("SELECT id FROM cities WHERE name =:name").params(name=city_name)
        ).scalar_one()
        sql_ = f"SELECT geometry FROM cities WHERE id = {city_id}"
        gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
        gdf.to_file(f"{city_name}.geojson")
