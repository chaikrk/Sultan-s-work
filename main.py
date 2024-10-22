from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image
import pytesseract

app = FastAPI()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Serve the index.html file
@app.get("/")
async def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # Load the image from the uploaded file
        image = Image.open(file.file)
        # Use PyTesseract to extract digits from the image
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        result = pytesseract.image_to_string(image, config=custom_config, lang='ara_number')

        return JSONResponse(content={"recognized_numeral": result.strip()})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


