from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = f"{PROJECT_ID}.bol_data"
DATASET_LOCATION = os.getenv("DATASET_LOCATION")
CREDS_FILE_PATH = os.getenv("CREDS_FILE_PATH")
