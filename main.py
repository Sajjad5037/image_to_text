import logging
from google.cloud import storage
from fastapi import HTTPException

# Ensure logging is set up at the start of your application
logging.basicConfig(level=logging.INFO)

def download_credentials_from_gcs():
    try:
        logging.info("Starting to download credentials from GCS...")

        # Initialize the GCS client
        storage_client = storage.Client()

        # Define the bucket and blob
        bucket_name = "credentials5037"
        blob_name = "dazzling-tensor-455512-j1-4569e9865ad0.json"
        
        logging.info(f"Fetching bucket {bucket_name} and blob {blob_name}.")

        # Access the bucket
        bucket = storage_client.get_bucket(bucket_name)

        # Access the blob (file)
        blob = bucket.blob(blob_name)
        
        # Define the local path where the file will be saved
        local_file_path = "/tmp/dazzling-tensor-455512-j1-4569e9865ad0.json"
        
        logging.info(f"Downloading {blob_name} to {local_file_path}.")

        # Download the file
        blob.download_to_filename(local_file_path)

        logging.info(f"Credentials downloaded successfully to {local_file_path}.")

    except Exception as e:
        logging.error(f"Error downloading credentials from GCS: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading credentials: {e}")
