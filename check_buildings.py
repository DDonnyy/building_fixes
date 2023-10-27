import json
import logging
import os
from datetime import datetime

import geopandas
import geopandas as gpd
import pandas as pd
import sqlalchemy as sa
from sklearn.neighbors import NearestNeighbors
from sqlalchemy import Engine

t = datetime.now().replace(microsecond=0)
formatted_time = t.strftime("%Y-%m-%d %H-%M-%S")
# log_file_name = f"building_fixes_{formatted_time}.log"
log_file_name = f"building_fixes.log"
logging.basicConfig(level=logging.INFO, filename=os.path.join(log_file_name),
                    format="%(asctime)s %(levelname)s %(message)s",encoding="UTF-8")


with open(os.getcwd() + "\config.json",encoding="UTF-8") as f:
    config_imputation = json.load(f)
    city = config_imputation["city"]
    sqlConnection = ["sqlConnection"]
    distance_limit = ["distance_limit"]


def save_cities_buildings_to_file(city_name: str, sql_alchemy_engine: Engine):
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text('SELECT id FROM cities WHERE name =:name').params(name=city_name)).scalar_one()
        sql_ = f"SELECT p.geometry, b.* FROM buildings b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
        gdf = gpd.read_postgis(
            sql_,
            conn,
            geom_col='geometry')
        gdf.to_file(f"buildings_{city_name}.geojson")


def save_city_to_file(city_name: str, sql_alchemy_engine: Engine):
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text('SELECT id FROM cities WHERE name =:name').params(name=city_name)).scalar_one()
        sql_ = f"SELECT geometry FROM cities WHERE id = {city_id}"
        gdf = gpd.read_postgis(
            sql_,
            conn,
            geom_col='geometry')
        gdf.to_file(f"{city_name}.geojson")


def save_cities_service_to_file(city_name: str, sql_alchemy_engine: Engine):
    with sql_alchemy_engine.connect() as conn:
        city_id: int = conn.execute(
            sa.text('SELECT id FROM cities WHERE name =:name').params(name=city_name)).scalar_one()
        sql_ = f"SELECT p.geometry, b.* FROM functional_objects b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
        gdf = gpd.read_postgis(
            sql_,
            conn,
            geom_col='geometry')
        gdf.to_file(f"services_{city_name}.geojson")


def search_neighbors_from_point(points_data: geopandas.GeoDataFrame, search_in_data: geopandas.GeoDataFrame, n_neigh,
                                radius) -> geopandas.GeoDataFrame:
    x = points_data.to_crs('EPSG:3857').geometry.centroid.apply(lambda point: point.x)
    y = points_data.to_crs('EPSG:3857').geometry.centroid.apply(lambda point: point.y)
    points = pd.DataFrame({"x": x, "y": y})
    x2 = search_in_data.to_crs('EPSG:3857').geometry.centroid.apply(lambda point: point.x)
    y2 = search_in_data.to_crs('EPSG:3857').geometry.centroid.apply(lambda point: point.y)
    buildings_points = pd.DataFrame({"x": x2, "y": y2})
    neigh = NearestNeighbors(n_neighbors=n_neigh, radius=radius)
    neigh.fit(buildings_points)
    neigh_dist, neigh_ind = neigh.kneighbors(points)
    neigh_ind = pd.Series(neigh_ind.tolist())

    # print((search_in_data.iloc[neigh_ind.explode()])["id"].explode().reset_index(drop=True))
    index = points_data.index
    points_data = points_data.reset_index(drop=True)
    points_data['closest_building_id'] = (search_in_data.iloc[neigh_ind.explode()])["physical_object_id"].explode().reset_index(
        drop=True)
    points_data = points_data.set_index(index)

    # rows_to_keep = neigh_ind.explode().unique()
    # search_in_data_filtered = search_in_data.iloc[rows_to_keep]

    return points_data


#engine = sa.create_engine(sqlConnection)

# save_cities_buildings_to_file(city, engine)
# save_cities_service_to_file(city, engine)

gdf = gpd.read_file(f"buildings_{city}.geojson")
gdf_geom_Points = gdf[gdf.geometry.type == 'Point'].copy()  # Выбрать строки, у которых геометрия типа Точка
gdf_geom_Polygons = gdf[gdf.geometry.type == 'Polygon'].copy()

gdf_geom_Points = search_neighbors_from_point(gdf_geom_Points, gdf_geom_Polygons, 1,
                                              5)  # добавлен столбец с ближайшим соседом не точкой

gdf_geom_Points = gdf_geom_Points.to_crs('EPSG:3857')
gdf_geom_Polygons = gdf_geom_Polygons.to_crs('EPSG:3857')
gdf_geom_Points["dist"] = (gdf_geom_Points.apply(
    lambda x: (x.geometry.distance((gdf_geom_Polygons.loc[
        gdf_geom_Polygons["physical_object_id"] == x['closest_building_id']]).geometry.boundary).explode().unique()), axis=1))

distance_limit = 30

gdf_geom_Points.apply(lambda x: logging.warning(f"\nСледующее здание-точка не имеет соседей на расстоянии {distance_limit}: "
                                                f"\n{x[:3].to_string()}\nРасстояние до ближайшего соседа = {x['dist']}\n{'':-^60}") if x['dist'] > distance_limit else None, axis=1)
gdf_geom_Points = gdf_geom_Points[gdf_geom_Points["dist"] < distance_limit]

gdf_services = gpd.read_file(f"services_{city}.geojson")
list_buildings_points = gdf_geom_Points["physical_object_id"].tolist()
gdf_services = gdf_services.query('physical_object_id in @list_buildings_points')
gdf_services["physical_object_id"] = gdf_services["physical_object_id"].apply(lambda x: gdf_geom_Points[gdf_geom_Points["physical_object_id"] == x]["closest_building_id"].explode().unique()[0])

print(gdf_services.to_string()) #Получили сервисы с привязкой к ближайшему зданию

#TODO удалить здания-точки (gdf_geom_Points) из DB, залить фикс сервисов

#Различные способы найти дистанцию в геометрии
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



#TODO разобрать с Folium

# gdf["coordinates"] = gdf.apply(lambda row: eval(row['coordinates']) , axis=1)
# gdf["coordinates"] = gdf.apply(lambda row: [(i[1], i[0]) for i in row['coordinates']], axis=1)
# gdf['geometry'] = gdf.apply(lambda row: Polygon(row['coordinates']), axis=1)
# map_ = folium.Map(zoom_start=10, crs='EPSG4326', tiles="CartoDB positron")
# m: folium.Map = gdf.explore(column='id', m=map_)
#
# map_.show_in_browser()
