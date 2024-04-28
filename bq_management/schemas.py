from google.cloud.bigquery import SchemaField
from .constants import DATASET_ID

REQUEST_DATA = {
    "table_id": f"{DATASET_ID}.request_data",
    "schema": [
        SchemaField(
            "retailer_id",
            "STRING",
            mode="REQUIRED",
            description=" bol retailer identity of the requesting client",
        ),
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
            "price",
            "FLOAT",
            mode="REQUIRED",
            description="price deviation of the product",
        ),
        SchemaField(
            "deviation",
            "FLOAT",
            mode="REQUIRED",
            description="deviation of price in percentage",
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
            "request_id",
            "STRING",
            mode="REQUIRED",
            description="Unique request identifier",
        ),
    ],
}


BOL_EAN_DATA = {
    "table_id": f"{DATASET_ID}.bol_ean_data",
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
            "retailer_id",
            "STRING",
            mode="nullAble",
            description="bol retailer id that requested job",
        ),
        SchemaField(
            "price",
            "FLOAT",
            mode="REQUIRED",
            description="price of the product",
        ),
        SchemaField(
            "job_id",
            "STRING",
            mode="REQUIRED",
            description="Unique request identifier",
        ),
    ],
}


BOL_OFFER_DATA = {
    "table_id": f"{DATASET_ID}.bol_offer_data",
    "schema": [
        SchemaField(
            "job_id",
            "STRING",
            mode="REQUIRED",
            description="Unique request identifier",
        ),
        SchemaField(
            "user_retailer_id",
            "STRING",
            mode="REQUIRED",
            description="bol retailer identity of the requesting client",
        ),
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
            "bol_offer_id",
            "STRING",
            mode="REQUIRED",
            description="BOL's offer id",
        ),
        SchemaField(
            "retailer_id",
            "STRING",
            mode="nullAble",
            description="BOL offer retailer name",
        ),
        SchemaField(
            "retailer_display_name",
            "STRING",
            mode="nullAble",
            description="BOL offer retailer name",
        ),
        SchemaField(
            "country_code",
            "STRING",
            mode="nullAble",
            description="Country code",
        ),
        SchemaField(
            "best_offer",
            "BOOL",
            mode="nullAble",
            description="Boolean representing best offer",
        ),
        SchemaField(
            "price",
            "FLOAT64",
            mode="REQUIRED",
            description="Price of the product",
        ),
        SchemaField(
            "deviation",
            "FLOAT",
            mode="REQUIRED",
            description="deviation of price in percentage",
        ),
        SchemaField(
            "fulfilment_method",
            "STRING",
            mode="NULLABLE",
            description="Fulfilment method of the product",
        ),
        SchemaField(
            "condition",
            "STRING",
            mode="NULLABLE",
            description="Offer conditions",
        ),
        SchemaField(
            "ultimate_order_time",
            "STRING",
            mode="NULLABLE",
            description="Ultimate order time",
        ),
        SchemaField(
            "min_delivery_date",
            "STRING",
            mode="NULLABLE",
            description="Minimum delivery date",
        ),
        SchemaField(
            "max_delivery_date",
            "STRING",
            mode="NULLABLE",
            description="Maximum delivery date",
        ),
    ],
}
