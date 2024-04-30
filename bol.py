import requests
import base64
import jwt
import time
from bq_management.intialize import client
from bq_management.schemas import REQUEST_DATA, BOL_EAN_DATA, BOL_OFFER_DATA
import functions_framework
from flask import make_response
import os
import logging
import time

logging.basicConfig(level=logging.INFO)


BOL_CLIENT_ID = (
    os.getenv("BOL_CLIENT_ID")
)
BOL_CLIENT_SECRET = (
    os.getenv("BOL_CLIENT_SECRET")
)

BOL_BASE_API_URL = (
    os.getenv("BOL_BASE_API_URL")
    if os.getenv("BOL_BASE_API_URL")
    else "https://api.bol.com"
)


def delete_records_from_bq(table_id, condition):
    """
    Deletes records from a BigQuery table based on a condition.

    Args:
    table_id (str): The ID of the table from which to delete records (in the format `your-project.your_dataset.your_table`).
    condition (str): The condition to use for deleting records (e.g., "id = 123").
    """
    query = f"""
    DELETE FROM `{table_id}`
    WHERE {condition}
    """

    query_job = client.query(query)
    query_job.result()

    print(f"Deleted records from {table_id} where {condition}")


def encode_base64(string):
    """
    A function that encodes a string to base64.

    Parameters:
    string (str): The string to be encoded.

    Returns:
    str: The encoded string in base64.
    """
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


def login_bol():
    """
    A function to handle the login process for the bol.com API.
    This function sends a POST request to the login endpoint with client credentials
    to obtain an access token for authentication.
    Returns the access token if the request is successful, otherwise logs an error.
    """
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
        logging.info(f"Error: {response.status_code} - {response.reason}")


def authorization_middleware(jwt_token):
    """
    A function that serves as an authorization middleware by decoding a JWT token,
    checking its expiration time, refreshing it if necessary, and returning the JWT token.

    Parameters:
    jwt_token (str): The JWT token to be decoded and validated.

    Returns:
    str: The validated and possibly refreshed JWT token.
    """
    decoded_token = jwt.decode(
        jwt_token, options={"verify_signature": False}, algorithms=["RS256"]
    )
    expiration_time = decoded_token["exp"]
    if time.time() > (expiration_time - 120):
        jwt_token = login_bol()
    return jwt_token


def is_within_threshold_percent(threshold, price, value):
    """
    Check if the given value is within a certain percentage threshold of the price.

    :param threshold: The percentage threshold within which the value should fall.
    :param price: The base price to compare against.
    :param value: The value to check if it falls within the threshold of the price.
    :return: True if the value is within the threshold range, False otherwise.
    """
    lower_bound = price - (threshold / 100 * price)
    upper_bound = price + (threshold / 100 * price)

    return lower_bound <= value <= upper_bound


def format_offer_data(offer, row):
    return {
        "price": offer["price"],
        "job_id": row.get("batch_id"),
        "EAN": row.get("EAN"),
        "user_retailer_id": row.get("retailer_id"),
        "client_id": row.get("client_id"),
        "bol_offer_id": offer.get("offerId"),
        "retailer_id": offer.get("retailerId"),
        "country_code": offer.get("countryCode"),
        "best_offer": offer.get("bestOffer"),
        "price": offer.get("price"),
        "fulfilment_method": offer.get("fulfilmentMethod"),
        "condition": offer.get("condition"),
        "ultimate_order_time": offer.get("ultimateOrderTime"),
        "min_delivery_date": offer.get("minDeliveryDate"),
        "max_delivery_date": offer.get("maxDeliveryDate"),
        "retailer_display_name": offer.get("retailer_display_name"),
        "deviation": row.get("deviation"),
        "min_articles": int(row.get("min_articles")),
    }


def process_offers(jwt_token, response_data, row, product_data):
    """
    Process offers based on response data, row, and product data.

    Parameters:
    response_data (dict): The response data containing offers.
    row (dict): The row data to compare prices.
    product_data (list): The list to store formatted offer data.
    """
    for offer in response_data.get("offers", []):
        if is_within_threshold_percent(row["deviation"], row["price"], offer["price"]):
            offer["retailer_display_name"] = fetch_retailer_info(
                jwt_token, offer.get("retailerId")
            )
            product_data.append(format_offer_data(offer, row))


def fetch_retailer_info(jwt_token, retailer_id):
    """
    A function to fetch retailer info provided JWT token and retailer_id.

    Parameters:
    - jwt_token (str): The JWT token for authentication.
    - retailer_id (int): Retailer id of product.
    """
    while True:
        api_url = f"{BOL_BASE_API_URL}/retailer/retailers/{retailer_id}"

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/vnd.retailer.v9+json",
            "Accept": "application/vnd.retailer.v9+json",
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            response_data = response.json()
            return response_data.get("displayName")

        except requests.RequestException as e:
            logging.info(f"Request error at retailer api: {e}")
            break  # Exit the loop in case of a request failure


def fetch_product_offers(jwt_token, product_data, row, page=1):
    """
    A function to fetch product offers using the provided JWT token and product data.

    Parameters:
    - jwt_token (str): The JWT token for authentication.
    - product_data (dict): Data related to the product.
    - row (dict): The row data containing product information.
    """
    while True:
        api_url = (
            f"{BOL_BASE_API_URL}/retailer/products/{row['EAN']}/offers?page={page}"
        )

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/vnd.retailer.v9+json",
            "Accept": "application/vnd.retailer.v9+json",
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            response_data = response.json()
            process_offers(jwt_token, response_data, row, product_data)

            # Check if there are still offers to fetch in the next page
            if len(response_data.get("offers", [])) == 50:
                page += 1
            else:
                break  # Exit the loop if there are no more pages

        except requests.RequestException as e:
            logging.info(f"Request error: {e}")
            break  # Exit the loop in case of a request failure


@functions_framework.http
def fetch_data_worker(request):
    """
    This function fetches data from a specified table, processes it, and inserts it into BigQuery.
    It uses a JWT token for authorization and includes a delay after every 5 iterations.
    Returns a response indicating the successful retrieval of data.
    """
    jwt_token = login_bol()
    counter = 0
    query = f"""
            SELECT *
            FROM `{REQUEST_DATA.get('table_id')}`
            LIMIT 500
        """

    query_job = client.query(query)
    for row in query_job:
        counter += 1
        jwt_token = authorization_middleware(jwt_token)
        product_data = []
        fetch_product_offers(jwt_token, product_data, row)
        processed_row = prepare_row_for_insertion(row)

        insert_into_bigquery(client, BOL_EAN_DATA.get("table_id"), [processed_row])
        if product_data:
            insert_into_bigquery(client, BOL_OFFER_DATA.get("table_id"), product_data)
        delete_records_from_bq(
            REQUEST_DATA.get("table_id"), f"request_id = '{row['request_id']}'"
        )

        # delay after 20 iterations
        # if counter % 20 == 0:
        #     time.sleep(30)

    return make_response("Retrieved the data from bol", 200)


def prepare_row_for_insertion(row):
    row_dict = dict(row)
    row_dict["job_id"] = row_dict["batch_id"]
    row_dict["min_articles"] = int(row_dict["min_articles"])
    for key in ["is_fetched", "batch_id", "request_id", "deviation"]:
        del row_dict[key]
    return row_dict


def insert_into_bigquery(client, table_id, data):
    errors = client.insert_rows_json(table_id, data)
    if errors:
        # pass
        logging.info(f"Errors occurred while inserting into {table_id}: {errors}")
