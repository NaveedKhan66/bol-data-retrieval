from google.cloud import bigquery
from .constants import DATASET_ID, PROJECT_ID, DATASET_LOCATION
import logging
from google.cloud import bigquery
from .schemas import REQUEST_DATA, BOL_EAN_DATA, BOL_OFFER_DATA
from google.api_core.exceptions import Conflict


logging.basicConfig(level=logging.INFO)
service_account_path = "optimistic-yeti-353713-eade4a9feeb0.json"
client = bigquery.Client.from_service_account_json(service_account_path)


def create_dataset():
    """Creats the main dataset on Biqquery"""

    dataset = bigquery.Dataset(DATASET_ID)
    dataset.location = DATASET_LOCATION
    try:
        dataset = client.create_dataset(dataset, timeout=30)
        logging.info(f"Dataset {DATASET_ID} created")
    except Conflict:
        logging.warning(f"Dataset {DATASET_ID} already exists")


def create_schema(schema):
    """Creates tables with defined schemas"""

    table_id = schema.get("table_id")

    schema = schema.get("schema")
    table = bigquery.Table(table_id, schema=schema)

    table = client.create_table(table, exists_ok=True)
    logging.info(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")


def load_schema():
    create_schema(REQUEST_DATA)
    create_schema(BOL_EAN_DATA)
    create_schema(BOL_OFFER_DATA)


# Run command in ROOT python -m bq_management.initialize
create_dataset()
load_schema()
