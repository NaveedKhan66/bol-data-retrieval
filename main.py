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
from bol import fetch_data_worker
import os

# Logging Config
logging.basicConfig(level=logging.INFO)


def read_xls(file_stream) -> DataFrame:
    df = pd.read_excel(file_stream)
    return dataframe_validation(df)


def bulk_insert(df: DataFrame, retailer_id, user_id):

    # Generate a unique batch_id
    batch_id = str(uuid.uuid4())

    client_id = user_id

    # Generate unique request_id for each row
    df["request_id"] = [str(uuid.uuid4()) for _ in range(len(df))]

    df["batch_id"] = batch_id
    df["is_fetched"] = False
    df["client_id"] = client_id
    df["retailer_id"] = retailer_id

    table_id = REQUEST_DATA.get("table_id")

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

        # SET GOOGLE_APPLICATION_CREDENTIALS env var for local setup to the path of cred file because to_gbq requires it
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDS_FILE_PATH
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
        user_id = request.args.get('user_id', default=None)  # Default to None if not provided
        if not user_id:
            return make_response("User is unauthenticated", 400)
        with open("index.html", "r") as file:
            html_content = file.read()
            
        hidden_field = f'<input type="hidden" id="user_id" name="user_id" value="{user_id}">'
        html_content = html_content.replace('</form>', f'{hidden_field}</form>')
        
        return make_response(html_content, 200)

    elif request.method == "POST":
        logging.info(f"Post request reached {request.form}")
        file = request.files["eanFile"]
        retailer_id = request.form["retailerId"]
        user_id = request.form["userId"]
        logging.info("User id: " + str(user_id))
        
        file_stream = BytesIO(file.read())
        df = read_xls(file_stream)

        bulk_insert(df, retailer_id, user_id)
        return make_response("File and data received", 200)
