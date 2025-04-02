import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import uvicorn
from google.cloud import storage
from fastapi.middleware.cors import CORSMiddleware
import logging

# Ensure logging is set up at the start of your application
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sajjadalinoor.vercel.app"],  # Explicitly allow only your frontend
    allow_credentials=True,  # Allow cookies/auth headers if needed
    allow_methods=["GET", "POST", "OPTIONS"],  # Limit allowed methods
    allow_headers=["Content-Type", "Authorization"],  # Specify necessary headers
)

storage_client = storage.Client()
# Google Cloud Storage bucket name
BUCKET_NAME = "pdf_url"

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

    
def upload_to_gcs(file: UploadFile):
    # Get the file content
    file_content = file.file.read()
    
    # Create a GCS bucket client
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # Generate a blob (file object) in the bucket
    blob = bucket.blob(file.filename)
    
    # Upload the file
    blob.upload_from_string(file_content, content_type=file.content_type)
    
    # Make the file publicly accessible (optional)
    blob.make_public()

    # Return the public URL of the uploaded file
    return blob.public_url
@app.post("/uploadPdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Upload the PDF file to Google Cloud Storage
        file_url = upload_to_gcs(file)
        
        # Return the public URL of the uploaded PDF
        return JSONResponse(status_code=200, content={"url": file_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

@app.post("/extractText")
async def extract_text(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")
    
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        extracted_text = pytesseract.image_to_string(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

    return JSONResponse(status_code=200, content={"extractedText": extracted_text})

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
