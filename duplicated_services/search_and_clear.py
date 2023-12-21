import json
import logging
import os

import pandas as pd

from db_utility import dbTools


def main():
    with open(os.path.join(os.path.dirname(__file__), "config.json"), encoding="UTF-8") as f:
        config_imputation = json.load(f)
        sql_connection = config_imputation["sqlConnection"]
        dry_run = config_imputation["dry_run"]
        service_ids = config_imputation["service_ids"]
    log_file_name = "search_and_clear.log"
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

    db = dbTools.DBworker(sql_connection)

    services_to_delete = pd.DataFrame()

    for service_id in service_ids:
        df = db.get_buildings_with_same_service(service_id)
        service_name = df["city_service_type"][0]
        grouped_df = df.groupby("building_id")

        logging.info(
            f"Filtering data based on service names ending with '(без названия)' for service id {service_id} {service_name}."
        )
        count = 0
        for key, item in grouped_df:
            rows_to_delete = item[item["service_name"].str.endswith(" без названия)")]
            if rows_to_delete.shape[0] == item.shape[0]:
                rows_to_delete = rows_to_delete.head(1)
                logging.info(
                    f"In the building with ID {item['building_id'].iloc[0]}, all services with ID {service_id} {service_name} have no names. Keeping only one."
                )
            services_to_delete = pd.concat(
                [services_to_delete, rows_to_delete.copy()], ignore_index=True
            )
            count += rows_to_delete.shape[0]
        logging.info(
            f"Found {count} services with id {service_id} {service_name} without name.",
        )
    logging.info(
        f"Found {services_to_delete.shape[0]} services for deletion at all.",
    )
    if services_to_delete.shape[0] == 0:
        exit()
    ids = set(services_to_delete["functional_object_id"].tolist())

    if dry_run:
        logging.info("The config specifies a dry run, data will not be saved.")
    else:
        db.remove_services(fuctional_object_ids=ids)


if __name__ == "__main__":
    main()
