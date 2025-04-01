import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract

app = FastAPI()

# Enable CORS (adjust allowed origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extractText")
async def extract_text(image: UploadFile = File(...)):
    # Ensure the uploaded file is an image
    print("DEBUG: Received file with content type:", image.content_type)
    if not image.content_type.startswith("image/"):
        print("DEBUG: File is not an image.")
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")
    
    try:
        # Read the uploaded file into memory
        contents = await image.read()
        print("DEBUG: Read file contents successfully. Size:", len(contents), "bytes")
        
        # Open the image using Pillow
        img = Image.open(io.BytesIO(contents))
        print("DEBUG: Image opened successfully. Format:", img.format)
        
        # Use pytesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(img)
        print("DEBUG: Extracted text:", extracted_text)
    except Exception as e:
        print("DEBUG: Exception occurred during processing:", e)
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

    return JSONResponse(status_code=200, content={"extractedText": extracted_text})
