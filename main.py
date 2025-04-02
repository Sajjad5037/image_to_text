import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import uvicorn
from google.cloud import storage

app = FastAPI()

# Allow frontend access (CORS configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sajjadalinoor.vercel.app"],  # Explicitly allow only your frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Limit allowed methods
    allow_headers=["Content-Type", "Authorization"],  # Specify necessary headers
)

# Google Cloud Storage bucket names
CREDENTIALS_BUCKET_NAME = "credentials5037"  # For storing credentials file
PDF_BUCKET_NAME = "pdf_bucket"  # For storing uploaded PDFs (change the name to your bucket)

# Function to download the credentials file from Google Cloud Storage
def download_credentials_from_gcs():
    try:
        # Create the GCS client
        storage_client = storage.Client()

        # Access the bucket and blob (file)
        bucket = storage_client.bucket(CREDENTIALS_BUCKET_NAME)
        blob = bucket.blob("dazzling-tensor-455512-j1-4569e9865ad0.json")  # Replace with your file name

        # Define the local path to save the credentials file
        local_credentials_path = "/tmp/google-credentials.json"
        
        # Download the file to the local path
        blob.download_to_filename(local_credentials_path)
        print(f"Downloaded credentials to {local_credentials_path}")

        # Set the environment variable to point to the downloaded credentials file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = local_credentials_path
        print("GOOGLE_APPLICATION_CREDENTIALS environment variable set.")
    
    except Exception as e:
        print(f"Error downloading credentials from GCS: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading credentials: {e}")

# Ensure the credentials are downloaded when the app starts
download_credentials_from_gcs()

# Create the Google Cloud Storage client using the provided credentials
storage_client = storage.Client()

def upload_to_gcs(file: UploadFile, bucket_name: str):
    try:
        print(f"Uploading file: {file.filename}, Content Type: {file.content_type}")

        # Read the file content
        file_content = file.file.read()
        print(f"Read {len(file_content)} bytes from the file.")

        # Create a GCS bucket client
        bucket = storage_client.bucket(bucket_name)
        print(f"Accessing bucket: {bucket_name}")

        # Generate a blob (file object) in the bucket
        blob = bucket.blob(file.filename)
        print(f"Generated blob for file: {file.filename}")

        # Upload the file content
        blob.upload_from_string(file_content, content_type=file.content_type)
        print(f"File uploaded to GCS as {file.filename}.")

        # Make the file publicly accessible (optional)
        blob.make_public()
        print(f"File {file.filename} is now publicly accessible.")

        # Return the public URL of the uploaded file
        public_url = blob.public_url
        print(f"File URL: {public_url}")
        return public_url

    except Exception as e:
        print(f"Error in upload_to_gcs: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

@app.post("/uploadPdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}, Content Type: {file.content_type}")

        # Upload the PDF file to the designated PDF bucket
        file_url = upload_to_gcs(file, PDF_BUCKET_NAME)
        print(f"File successfully uploaded, returning URL: {file_url}")

        # Return the public URL of the uploaded PDF
        return JSONResponse(status_code=200, content={"url": file_url})

    except Exception as e:
        print(f"Error in upload_pdf: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

@app.post("/extractText")
async def extract_text(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")
    
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))

        # Extract text from the image using pytesseract
        extracted_text = pytesseract.image_to_string(img)
        print(f"Extracted Text: {extracted_text}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

    return JSONResponse(status_code=200, content={"extractedText": extracted_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get PORT from environment variable or default to 5000
    uvicorn.run(app, host="0.0.0.0", port=port)
