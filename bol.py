import requests
import base64
import jwt
import time
from bq_management.intialize import client
from bq_management.schemas import REQUEST_DATA, BOL_EAN_DATA, BOL_OFFER_DATA
import functions_framework
from flask import make_response
import os

BOL_CLIENT_ID = os.getenv("BOL_CLIENT_ID")
BOL_CLIENT_SECRET = os.getenv("BOL_CLIENT_SECRET")

BOL_BASE_API_URL = os.getenv("BOL_BASE_API_URL")


def encode_base64(string):
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


def login_bol():
    api_url = "https://login.bol.com/token?grant_type=client_credentials"

    bearer_token = encode_base64(f"{BOL_CLIENT_ID}:{BOL_CLIENT_SECRET}")

    headers = {
        "Authorization": f"Basic {bearer_token}",
        "Content-Type": "application/json",
    }

    request_data = {}

    response = requests.post(api_url, headers=headers, json=request_data)

    if response.ok:
        response_data = response.json()
        return response_data["access_token"]
    else:
        print(f"Error: {response.status_code} - {response.reason}")


def Authorization_middleware(jwt_token):
    decoded_token = jwt.decode(
        jwt_token, options={"verify_signature": False}, algorithms=["RS256"]
    )
    expiration_time = decoded_token["exp"]
    if time.time() > (expiration_time - 120):
        jwt_token = login_bol()
    return jwt_token


def is_within_threshold_percent(threshold, price, value):
    lower_bound = price - (threshold * price)
    upper_bound = price + (threshold * price)

    return lower_bound <= value <= upper_bound


def format_offer_data(offer, row):
    return {
        "price": offer["price"],
        "job_id": row["batch_id"],
        "bol_offer_id": offer["offerId"],
        "retailer_id": offer["retailerId"],
        "country_code": offer["countryCode"],
        "best_offer": offer["bestOffer"],
        "price": offer["price"],
        "fulfilment_method": offer["fulfilmentMethod"],
        "condition": offer["condition"],
        "ultimate_order_time": offer["ultimateOrderTime"],
        "min_delivery_date": offer["minDeliveryDate"],
        "max_delivery_date": offer["maxDeliveryDate"],
    }


def process_offers(response_data, row, product_data):
    for offer in response_data.get("offers", []):
        if is_within_threshold_percent(0.1, row["price"], offer["price"]):
            product_data.append(format_offer_data(offer, row))


def fetch_product_offers(jwt_token, product_data, row, page=1):
    api_url = f"{BOL_BASE_API_URL}/retailer/products/{row['EAN']}/offers?page={page}"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/vnd.retailer.v9+json",
        "Accept": "application/vnd.retailer.v9+json",
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        process_offers(response_data, row, product_data)
        print("This is response_data", response_data)
        if len(response_data.get("offers", [])) == 50:
            fetch_product_offers(jwt_token, row, product_data, page + 1)

    except requests.RequestException as e:
        print(f"Request error: {e}")


@functions_framework.http
def fetch_data_worker(request):
    jwt_token = login_bol()
    print(jwt_token)

    query = f"""
            SELECT *
            FROM `{REQUEST_DATA.get('table_id')}`
            LIMIT 500
        """

    query_job = client.query(query)
    for row in query_job:

        jwt_token = Authorization_middleware(jwt_token)
        print("request_id=======>: ", row["request_id"])
        product_data = []
        fetch_product_offers(jwt_token, product_data, row)
        processed_row = prepare_row_for_insertion(row)

        print(product_data, "product_data")

        insert_into_bigquery(client, BOL_EAN_DATA.get("table_id"), [processed_row])
        if product_data:
            insert_into_bigquery(client, BOL_OFFER_DATA.get("table_id"), product_data)

    return make_response("File and data received", 200)


def prepare_row_for_insertion(row):
    row_dict = dict(row)
    row_dict["job_id"] = row_dict["batch_id"]
    for key in ["is_fetched", "request_id", "batch_id", "retailer_id"]:
        del row_dict[key]
    return row_dict


def insert_into_bigquery(client, table_id, data):
    errors = client.insert_rows_json(table_id, data)
    if errors:
        print(f"Errors occurred while inserting into {table_id}:", errors)
