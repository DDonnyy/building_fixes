import json
import logging
import os
from datetime import datetime
import geopandas as gpd
import pandas as pd
import sqlalchemy as sa
from tqdm import tqdm
from sklearn.neighbors import NearestNeighbors


def save_cities_buildings_to_file(city_name: str, sql_alchemy_engine: sa.Engine):
    logging.info(f"Downloading {city_name}'s building to file")
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text("SELECT id FROM cities WHERE name =:name").params(name=city_name)
        ).scalar_one()
        sql_ = f"SELECT p.geometry, b.* FROM buildings b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
        gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
        gdf.to_file(f"buildings_{city_name}.geojson")
    logging.info("Done!\n")


def save_cities_service_to_file(city_name: str, sql_alchemy_engine: sa.Engine):
    logging.info(f"Downloading {city_name}'s services to file")
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text("SELECT id FROM cities WHERE name =:name").params(name=city_name)
        ).scalar_one()
        sql_ = f"SELECT p.geometry, b.* FROM functional_objects b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
        gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
        gdf.to_file(f"services_{city_name}.geojson")
    logging.info("Done!\n")


def search_neighbor_from_point_buffer(
    points_data: gpd.GeoDataFrame, search_in_data: gpd.GeoDataFrame, radius
) -> gpd.GeoDataFrame:
    search_in_data = search_in_data.to_crs("EPSG:3857")
    points_data = points_data.to_crs("EPSG:3857")
    logging.info("Searching for building-points neighbors")
    join = gpd.sjoin_nearest(
        points_data,
        search_in_data,
        how="inner",
        max_distance=radius,
        distance_col="dist",
    )
    points_data["closest_building_physical_id"] = join["physical_object_id_right"]
    logging.info("Done!\n")
    return points_data


def upload_services_db(sql_alchemy_engine: sa.Engine, data: gpd.GeoDataFrame):
    logging.info(f"Updating services in DB")
    with sql_alchemy_engine.connect() as connection:
        for ind, row in data.iterrows():
            id_value = row["id"]
            new_physical_object_id = row["physical_object_id"]

            stmt = (
                sa.update("functional_objects")
                .where("id" == id_value)
                .values(
                    physical_object_id=new_physical_object_id, updated_at=datetime.now()
                )
            )
            connection.execute(stmt)
            connection.commit()
    logging.info("Done!\n")


def remove_building_db(sql_alchemy_engine: sa.Engine, data: gpd.GeoDataFrame):
    logging.info(f"Removing redundant building-points in DB")
    with sql_alchemy_engine.connect() as connection:
        for _, row in data.iterrows():
            building_id = row["id"]
            physical_object_id = row["physical_object_id"]
            stmt = f"DELETE FROM buildings WHERE id = {building_id}"
            connection.execute(stmt)
            stmt = f"DELETE FROM physical_objects WHERE id = {physical_object_id}"
            connection.execute(stmt)
            connection.commit()
    logging.info("Done!\n")


def main():
    log_file_name = f"building_fixes.log"
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

    with open(os.path.join(os.getcwd(), "config.json"), encoding="UTF-8") as f:
        config_imputation = json.load(f)
        city = config_imputation["city"]
        sql_connection = config_imputation["sqlConnection"]
        distance_limit = config_imputation["distance_limit"]
        dry_run = config_imputation["dry_run"]
        from_file = config_imputation["from_file"]

    engine = sa.create_engine(sql_connection)
    if not from_file:
        save_cities_buildings_to_file(city, engine)
        save_cities_service_to_file(city, engine)

    logging.info(f"Reading {city}'s services file")
    gdf_services: gpd.GeoDataFrame = gpd.read_file(f"services_{city}.geojson")
    logging.info(f"Done!\n")

    logging.info(f"Reading {city}'s building file")
    gdf_buildings: gpd.GeoDataFrame = gpd.read_file(f"buildings_{city}.geojson")
    logging.info(f"Done!\n")

    # Выбрать строки, у которых геометрия типа Точка и полигон
    gdf_geom_points = gdf_buildings[gdf_buildings.geometry.type == "Point"].copy()
    gdf_geom_polygons = gdf_buildings[gdf_buildings.geometry.type == "Polygon"].copy()

    gdf_geom_points = search_neighbor_from_point_buffer(
        gdf_geom_points, gdf_geom_polygons, distance_limit
    )  # добавлен столбец с ближайшим соседом не точкой

    gdf_geom_points.loc[gdf_geom_points["closest_building_physical_id"].isnull()].apply(
        lambda x: logging.warning(
            f"\nNext building-point don't have neighbors in distance = {distance_limit}: "
            f"\n{x[:3].to_string()}\n{'':-^60}"
        ),
        axis=1,
    )
    points_amount = gdf_geom_points.shape[0]

    # Точки, которые надо удалить из бд
    gdf_geom_points = gdf_geom_points.dropna(subset=["closest_building_physical_id"])
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
    logging.warning(
        f'In the city of "{city}", neighbors were found at a distance of {distance_limit} for {points_amount_to_change} out of {points_amount} building points.'
    )
    if not dry_run:
        upload_services_db(engine, gdf_services)
        remove_building_db(engine, gdf_geom_points)
    else:
        logging.info("The config specifies a dry run, so the data will not be saved.")


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