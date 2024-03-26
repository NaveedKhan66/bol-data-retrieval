# Local Setup and Run Instructions

This README provides instructions on how to set up and run the function locally for testing

## Steps to Run Locally

1. **Change Project ID**:
    - Navigate to the `bq_management.constants` file.
    - Modify the `PROJECT_ID` to reflect your Google Cloud project ID.

2. **Initialize BigQuery**:
    - Run the `initialize` file to set up your BigQuery database.

3. **Export Environment Variable on macOS**:
    - If you are on a macOS system, export the following environment variable to handle the fork safety issue.
    - Open your terminal and run:
      ```
      export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
      ```

4. **Start the Cloud Function Locally**:
    - Run the Functions Framework targeting your function.
    - Use the following command:
      ```
      functions-framework --target=request_form
      ```

5. **Accessing the Local Cloud Function**:
    - With the Cloud Function running, you can access the form locally.
    - Open a web browser and navigate to `localhost:8080`.

6. **Interacting with the Form**:
    - Use the form on the local web page to insert data into BigQuery.

