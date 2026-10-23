Python


import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from PIL import Image
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

@app.get("/")
def home():
    return {"status": "Serwer AI Hot Wheels działa!"}

@app.post("/api/v1/scan")
async def scan_car(file: UploadFile = File(...)):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Brak klucza GEMINI_API_KEY na serwerze!")
    
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = (
            "Rozpoznaj ten model resoraka Hot Wheels ze zdjęcia. "
            "Podaj wyłącznie dokładną, pełną nazwę modelu i serii (np. 'Hot Wheels Nissan Skyline GT-R R34'). "
            "Żadnych dodatkowych słów, tylko sama czysta nazwa."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt]
        )

        detected_car = response.text.strip() if response.text else "Hot Wheels Unknown Model"

        # Generowanie ceny i linków
        let_hash = sum(ord(c) for c in detected_car)
        base_price = (let_hash % 120) + 30
        encoded_query = detected_car.replace(" ", "+")

        return {
            "success": True,
            "car_name": detected_car,
            "price": base_price,
            "ebay_sold": f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}&LH_Complete=1&LH_Sold=1&_sop=13"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))