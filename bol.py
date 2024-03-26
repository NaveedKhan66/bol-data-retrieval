import requests
import base64
import jwt
import time
from bq_management.intialize import client
from bq_management.schemas import REQUEST_DATA,BOL_EAN_DATA,BOL_OFFER_DATA

BOL_CLIENT_ID = "c8946e8c-06fb-447f-aad6-f143496fcc18"
BOL_CLIENT_SECRET = "Bl!ZfisCwDKON!+83ZG7fTMld!Kozbp2qQ0k7t?kCia7wfkgS)Kb13twdycbdcPD"

BOL_BASE_API_URL = "https://api.bol.com"


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
    decoded_token = jwt.decode(jwt_token, verify=False)
    expiration_time = decoded_token["exp"]

    if time.time() > expiration_time:
        jwt_token = login_bol()
    return jwt_token


jwt_token = login_bol()


def is_within_threshold_percent(threshold, price, value):
    lower_bound = price - (threshold * price)
    upper_bound = price + (threshold * price)

    return lower_bound <= value <= upper_bound


data = []


def get_filtered_products(jwt_token,row, page=1):
    api_url = f"{BOL_BASE_API_URL}/retailer/products/{row['EAN']}/offers?page={page}"
    print(api_url, "api_url")

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/vnd.retailer.v9+json",
        "Accept": "application/vnd.retailer.v9+json",
    }

    response = requests.get(
        api_url,
        headers=headers,
    )

    if response.ok:
        response_data = response.json()
        print(response_data)
        if response_data:
            for offer in response_data["offers"]:
                if is_within_threshold_percent(0.1, row['price'], offer["price"]):
                    data.append({
                        'price':offer['price'],
                        'job_id':row['batch_id'],
                        'bol_offer_id':offer['offerId'],
                        'retailer_id':offer['retailerId'],
                        'country_code':offer['countryCode'],
                        'best_offer':offer['bestOffer'],
                        'price':offer['price'],
                        'fulfilment_method':offer['fulfilmentMethod'],
                        'condition':offer['condition'],
                        'ultimate_order_time':offer['ultimateOrderTime'],
                        'min_delivery_date':offer['minDeliveryDate'],
                        'max_delivery_date':offer['maxDeliveryDate'],
                    })
            if len(response_data["offers"]) == 50:
                get_filtered_products(jwt_token, row, page + 1)
    else:
        print(f"Error: {response.status_code} - {response.reason}")


print(jwt_token, "jwt_token")
# get_filtered_products(jwt_token, "8712799411319", 40)


def fetch_data_worker():
    # while True:
        query = f"""
            SELECT *
            FROM `{REQUEST_DATA.get('table_id')}`
            LIMIT 10
        """

        query_job = client.query(query)
        for row in query_job:
            print('request_id=======>: ',row['request_id'])
            get_filtered_products(jwt_token,row)
            row= dict(row)
            row['job_id']=row['batch_id']
            client.insert_rows_json( BOL_EAN_DATA.get('table_id'), [row])
            client.insert_rows_json( BOL_OFFER_DATA.get('table_id'), [data])
            data=[]



print(data, "data")

fetch_data_worker()