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

def upload_to_gcs(file: UploadFile):
    try:
        # Print file information for debugging
        print(f"Uploading file: {file.filename}, Content Type: {file.content_type}")

        # Get the file content
        file_content = file.file.read()
        print(f"Read {len(file_content)} bytes from the file.")

        # Create a GCS bucket client
        bucket = storage_client.bucket(BUCKET_NAME)
        print(f"Accessing bucket: {BUCKET_NAME}")

        # Generate a blob (file object) in the bucket
        blob = bucket.blob(file.filename)
        print(f"Generated blob for file: {file.filename}")

        # Upload the file
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

        # Upload the PDF file to Google Cloud Storage
        file_url = upload_to_gcs(file)
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
        extracted_text = pytesseract.image_to_string(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

    return JSONResponse(status_code=200, content={"extractedText": extracted_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get PORT from Heroku
    uvicorn.run(app, host="0.0.0.0", port=port)
