from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


PROJECT_ID = os.getenv("PROJECT_ID") if os.getenv("PROJECT_ID") else "central-eon-418013"
DATASET_ID = f"{PROJECT_ID}.bol_data"
DATASET_LOCATION = os.getenv("DATASET_LOCATION") if os.getenv("DATASET_LOCATION") else "US"
CREDS_FILE_PATH = os.getenv("CREDS_FILE_PATH") if os.getenv("CREDS_FILE_PATH") else "central-eon-418013-75fbe0bbb690.json"
