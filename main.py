import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sajjadalinoor.vercel.app"],  # Explicitly allow only your frontend
    allow_credentials=True,  # Allow cookies/auth headers if needed
    allow_methods=["GET", "POST", "OPTIONS"],  # Limit allowed methods
    allow_headers=["Content-Type", "Authorization"],  # Specify necessary headers
)

@app.post("/extractText")
async def extract_text(image: UploadFile = File(...)):
    print("Request received: extractText")  # Debugging statement
    if not image.content_type.startswith("image/"):
        print(f"Invalid file type received: {image.content_type}")  # Debugging statement
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")
    
    try:
        contents = await image.read()
        print(f"Image size (bytes): {len(contents)}")  # Debugging statement
        img = Image.open(io.BytesIO(contents))
        print("Image opened successfully")  # Debugging statement
        extracted_text = pytesseract.image_to_string(img)
        print("Text extraction complete")  # Debugging statement
    except Exception as e:
        print(f"Error processing image: {e}")  # Debugging statement
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

    print("Text extraction finished. Returning response.")  # Debugging statement
    return JSONResponse(status_code=200, content={"extractedText": extracted_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Correct port setup for Heroku
    print(f"Starting server on port {port}")  # Debugging statement
    uvicorn.run(app, host="0.0.0.0", port=port)
