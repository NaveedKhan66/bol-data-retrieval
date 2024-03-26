import pandas as pd
import uuid
from pandas_gbq import to_gbq
from bq_management.constants import PROJECT_ID, CREDS_FILE_PATH
from bq_management.schemas import REQUEST_DATA
from utils import dataframe_validation
from pandas import DataFrame
import functions_framework
from flask import make_response
import logging
from io import BytesIO
import os

# Logging Config
logging.basicConfig(level=logging.INFO)


def read_xls(file_stream) -> DataFrame:
    df = pd.read_excel(file_stream)
    return dataframe_validation(df)


def bulk_insert(df: DataFrame, retailer_id):

    # Generate a unique batch_id
    batch_id = str(uuid.uuid4())

    # TODO: Get client_id from the form
    client_id = str(uuid.uuid4())

    # Generate unique request_id for each row
    df["request_id"] = [str(uuid.uuid4()) for _ in range(len(df))]

    df["batch_id"] = batch_id
    df["is_fetched"] = False
    df["client_id"] = client_id
    df["retailer_id"] = retailer_id

    table_id = REQUEST_DATA.get("table_id")

    # SET GOOGLE_APPLICATION_CREDENTIALS env var to the path of cred file before running this
    # to_gbq(df, table_id, project_id=PROJECT_ID, if_exists="append", progress_bar=True)

    BATCH_SIZE = 1000
    total_rows = len(df)
    num_batches = (total_rows // BATCH_SIZE) + (
        1 if total_rows % BATCH_SIZE != 0 else 0
    )

    for i in range(num_batches):
        start_idx = i * BATCH_SIZE
        end_idx = min(
            start_idx + BATCH_SIZE, total_rows
        )  # Ensure not to exceed df length
        df_batch = df.iloc[start_idx:end_idx]

        # SET GOOGLE_APPLICATION_CREDENTIALS env var to the path of cred file because to_gbq requires it
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDS_FILE_PATH
        # Appending the batch
        to_gbq(
            df_batch,
            table_id,
            project_id=PROJECT_ID,
            if_exists="append",
            progress_bar=True,
        )

        logging.info(f"Batch {i+1}/{num_batches} inserted to BigQuery.")


@functions_framework.http
def request_form(request):
    if request.method == "GET":
        # Read HTML content from index form file
        with open("index.html", "r") as file:
            html_content = file.read()
        return make_response(html_content, 200)

    elif request.method == "POST":
        file = request.files["eanFile"]
        retailer_id = request.form["retailerId"]
        file_stream = BytesIO(file.read())
        df = read_xls(file_stream)

        bulk_insert(df, retailer_id)
        return make_response("File and data received", 200)
