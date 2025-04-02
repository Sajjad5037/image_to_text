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
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
