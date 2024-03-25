from google.cloud.bigquery import SchemaField
from .constants import DATASET_ID, PROJECT_ID

REQUEST_DATA = {
    "table_id": f"{DATASET_ID}.request_data" ,
    "schema": [
        SchemaField(
            "client_id",
            "STRING",
            mode="REQUIRED",
            description="client identity of the requesting client",
        ),
        SchemaField(
            "EAN", "INTEGER", mode="REQUIRED", description="EAN of the BOL product"
        ),
        SchemaField(
            "price", "FLOAT", mode="REQUIRED", description="price deviation of the product"
        ),
        SchemaField(
            "batch_id",
            "STRING",
            mode="REQUIRED",
            description="Batch identifier for a single file",
        ),
        SchemaField(
            "is_fetched",
            "BOOLEAN",
            mode="REQUIRED",
            description="True if the request data is fetched, False otherwise",
            default_value_expression="FALSE",
        ),
        SchemaField(
            "request_id", "STRING", mode="REQUIRED", description="Unique request identifier"
        ),
    ]

}