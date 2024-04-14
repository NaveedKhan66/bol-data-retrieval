
# Cloud Functions for BigQuery Operations

This project includes two main Cloud Functions:
1. `request_form`: A function that serves an HTML form and processes file uploads to insert data into BigQuery.
2. `fetch_data_worker`: A function that fetches data from `bol.com` based on the entries in BigQuery and updates the dataset.

## Local Setup Instructions

### Prerequisites
- Google Cloud Platform account and a BigQuery dataset.
- Python 3 environment.

### Steps

1. **Clone the Repository**
   ```
   git clone [Your-Repository-URL]
   ```

2. **Create a Python Virtual Environment**
   ```bash
   python3 -m venv env
   source ./env/bin/activate
   ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Service Account Credentials**
   - Obtain a service account JSON key file from Google Cloud Console.
   - Set the environment variable for local development:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="[PATH_TO_YOUR_SERVICE_ACCOUNT_FILE]"
     ```
   - If you are using macOS, set the following flag to handle multi-threading issues:
     ```bash
     export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
     ```

5. **Modify Local Configuration Files**
   - Update `bq_management/constants.py` with your `PROJECT_ID` and other constants.
   - Ensure `bq_management/initialize.py` is set with the appropriate service account path if needed.
   - Adjust the URL in `index.html` to point to `localhost:8080`.

6. **Running the `request_form` Function Locally**
   ```bash
   functions-framework --target=request_form --port=8080
   ```
   - Access the form via: `http://localhost:8080?user_id=<some_test_user_id>`

7. **Running the `fetch_data_worker` Function Locally**
   ```bash
   functions-framework --target=fetch_data_worker --port=8081
   ```
   - Trigger the function by accessing: `http://localhost:8081`

## Deployment Instructions

1. **Prepare for Deployment**
   - Ensure the use of the credentials file path is commented out in `bq_management/initialize.py`.

2. **Deploy `request_form` Cloud Function**
   ```bash
   gcloud functions deploy request_form --gen2 \
   --runtime=python310 --source=. \
   --allow-unauthenticated --trigger-http \
   --env-vars-file=.env.yaml --service-account=your-service-account@gcp.com
   ```

3. **Set Up Pub/Sub Trigger**
   - Create a Pub/Sub topic to trigger the `fetch_data_worker` function based on your schedule.

4. **Deploy `fetch_data_worker` Cloud Function**
   ```bash
   gcloud functions deploy fetch_data_worker --gen2 \
   --runtime=python310 \
   --allow-unauthenticated --trigger-topic=your-trigger-topic-name \
   --env-vars-file=.env.yaml --service-account=your-service-account@gcp.com
   ```

## Additional Notes
- Ensure you have the appropriate permissions to deploy resources in Google Cloud Platform.
- Review all environment-specific settings and credentials before starting the deployment process.
- Regularly update and maintain the security of your service account keys and environment configurations.
