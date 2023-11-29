import logging
from datetime import datetime
import geopandas as gpd
import sqlalchemy as sa
import pandas as pd

from DButility import mapping


class DBworker:
    def __init__(
        self,
        sql_connection: str,
    ):
        logging.info(f"Initializing DBworker with SQL connection {sql_connection}")
        self.engine = sa.create_engine(sql_connection)
        logging.info(f"Successfully connected!")

    def refresh_materialized_view(self, name: str):
        logging.info(f"Refreshing materialized view {name}")
        with self.engine.connect() as conn:
            conn.execute(sa.text(f"REFRESH MATERIALIZED VIEW {name}"))
        logging.info("Done refreshing!")

    def get_buildings_with_same_service(self, service_id: int):
        logging.info(
            f"Fetching buildings with multiple occurrences of the same service type for service_id: {service_id}"
        )
        with self.engine.connect() as conn:
            table = mapping.t_all_services
            stmt = sa.select(
                table.c.service_name, table.c.building_id, table.c.city_service_type
            ).where(
                table.c.building_id.in_(
                    sa.select(sa.distinct(table.c.building_id))
                    .where(table.c.city_service_type_id == service_id)
                    .group_by(table.c.building_id)
                    .having(sa.func.count("*") > 1)
                )
                & (table.c.city_service_type_id == service_id)
            )
            df = pd.read_sql(stmt, conn)
            logging.info("Done fetching!")
        return df

    def remove_services(self, fuctional_object_ids: set):
        logging.info(f"Removing the found services.")
        with self.engine.connect() as conn:
            for obj_id in fuctional_object_ids:
                stmt = sa.delete(mapping.FunctionalObject).where(
                    mapping.FunctionalObject.id == obj_id
                )
                conn.execute(stmt)
            conn.commit()
        logging.info("Done removing!")
        self.refresh_materialized_view("all_services")
        return

    def download_services(self, city_name: str, save: bool):
        logging.info(f"Downloading {city_name}'s services")
        with self.engine.connect() as conn:
            city_id: int = conn.execute(
                sa.text("SELECT id FROM cities WHERE name =:name").params(
                    name=city_name
                )
            ).scalar_one()
            sql_ = f"SELECT p.geometry, b.* FROM functional_objects b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
            gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
            if save:
                gdf.to_file(f"data/services_{city_name}.geojson")
        logging.info("Done downloading services!\n")
        return gdf

    def download_buildings(self, city_name: str, save: bool):
        logging.info(f"Downloading {city_name}'s building")
        with self.engine.connect() as conn:
            city_id: int = conn.execute(
                sa.text("SELECT id FROM cities WHERE name =:name").params(
                    name=city_name
                )
            ).scalar_one()
            sql_ = f"SELECT p.geometry, b.* FROM buildings b JOIN physical_objects p ON b.physical_object_id = p.id WHERE p.city_id = {city_id}"
            gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
            if save:
                gdf.to_file(f"data/buildings_{city_name}.geojson")
        logging.info("Done downloading building!\n")
        return gdf

    def remove_building(self, data: gpd.GeoDataFrame):
        logging.info(f"Removing redundant building-points in DB")
        with self.engine.connect() as connection:
            for _, row in data.iterrows():
                building_id = row["id"]
                physical_object_id = row["physical_object_id"]
                stmt = sa.delete(mapping.Building).where(
                    mapping.Building.id == building_id
                )
                connection.execute(stmt)

                stmt = sa.delete(mapping.PhysicalObject).where(
                    mapping.PhysicalObject.id == physical_object_id
                )
                connection.execute(stmt)
            connection.commit()
        logging.info("Done removing!\n")

    def upload_services(self, data: gpd.GeoDataFrame):
        logging.info(f"Updating services in DB")
        with self.engine.connect() as connection:
            for ind, row in data.iterrows():
                id_value = row["id"]
                new_physical_object_id = row["physical_object_id"]

                stmt = (
                    sa.update(mapping.FunctionalObject)
                    .where(mapping.FunctionalObject.id == id_value)
                    .values(
                        physical_object_id=new_physical_object_id,
                        updated_at=datetime.now(),
                    )
                )
                connection.execute(stmt)
            connection.commit()
        logging.info("Done updating!\n")

    def save_city_to_file(self, city_name: str):
        with self.engine.connect() as conn:
            city_id: int = conn.execute(
                sa.text("SELECT id FROM cities WHERE name =:name").params(
                    name=city_name
                )
            ).scalar_one()
            sql_ = f"SELECT geometry FROM cities WHERE id = {city_id}"
            gdf = gpd.read_postgis(sql_, conn, geom_col="geometry")
            gdf.to_file(f"{city_name}.geojson")
