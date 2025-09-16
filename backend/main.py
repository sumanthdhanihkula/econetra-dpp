<<<<<<< HEAD
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson.objectid import ObjectId
from database import db
from models.dpp import DPP

app = FastAPI(title="Econetra DPP API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Check ---
@app.get("/status")
async def get_status():
    return {"status": "OK"}

# --- Root ---
@app.get("/")
async def root():
    return {"message": "Econetra DPP API up"}

# --- Create DPP ---
@app.post("/dpp", status_code=201)
async def create_dpp(dpp: DPP):
    doc = dpp.dict()
    result = await db.dpps.insert_one(doc)
    return {"id": str(result.inserted_id)}

# --- List DPPs ---
@app.get("/dpp")
async def list_dpps(limit: int = 50):
    cursor = db.dpps.find().sort([("_id", -1)]).limit(limit)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return items

# --- Get single DPP ---
@app.get("/dpp/{dpp_id}")
async def get_dpp(dpp_id: str):
    try:
        oid = ObjectId(dpp_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid DPP id")
    record = await db.dpps.find_one({"_id": oid})
    if not record:
        raise HTTPException(status_code=404, detail="DPP not found")
    record["id"] = str(record["_id"])
    record.pop("_id", None)
    return record

# --- Update DPP ---
@app.put("/dpp/{dpp_id}")
async def update_dpp(dpp_id: str, dpp: DPP):
    try:
        oid = ObjectId(dpp_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid DPP id")

    update_data = {k: v for k, v in dpp.dict().items() if v is not None}
    result = await db.dpps.update_one({"_id": oid}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="DPP not found")

    return {"message": "DPP updated", "id": dpp_id}

# --- Delete DPP ---
@app.delete("/dpp/{dpp_id}")
async def delete_dpp(dpp_id: str):
    try:
        oid = ObjectId(dpp_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid DPP id")
    result = await db.dpps.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="DPP not found")
    return {"message": "DPP deleted", "id": dpp_id}
=======
# backend/main.py
from fastapi import FastAPI, UploadFile, File
import pytesseract
from PIL import Image
import io
import os
import json
import openai
import re

app = FastAPI()

# --- Tesseract setup (Windows default path) ---
# If you installed tesseract in another location, update the path below.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- OpenAI setup ---
openai.api_key = os.getenv("OPENAI_API_KEY")  # make sure this env var is set

# --- Prompt / Schema we want the LLM to return ---
DPP_SCHEMA_PROMPT = """
You are an assistant that converts messy invoice text into a JSON matching the DPP schema below.
Return only VALID JSON and nothing else (no explanation, no extra text).

Schema:
{
  "product_id": "string or null",
  "product_name": "string or null",
  "category": "string or null",
  "material_composition": "string or null",
  "batch_number": "string or null",
  "supplier": {
    "name": "string or null",
    "address": "string or null",
    "contact": "string or null"
  },
  "manufacture_date": "string (YYYY-MM-DD) or null",
  "expiry_date": "string (YYYY-MM-DD) or null",
  "certifications": ["string", "..."] or [],
  "sustainability_score": "string or null",
  "invoice_details": {
    "invoice_number": "string or null",
    "invoice_date": "string or null",
    "quantity": integer or null,
    "price": float or null,
    "currency": "string or null"
  },
  "traceability": {
    "origin_country": "string or null",
    "factory_location": "string or null",
    "transport_mode": "string or null"
  }
}

If a field cannot be found, set it to null (or [] for lists). Use best-effort parsing from the invoice text.
Invoice text:
{raw_text}
"""

@app.get("/")
def home():
    return {"message": "Hello Econetra - Digital Product Passport API"}

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    # 1) Read image bytes and run OCR
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        return {"error": "Uploaded file is not a valid image or cannot be opened.", "details": str(e)}

    raw_text = pytesseract.image_to_string(image)

    # 2) Prepare final prompt
    prompt = DPP_SCHEMA_PROMPT.format(raw_text=raw_text)

    # 3) Call OpenAI (chat completion)
    if not openai.api_key:
        return {"error": "OPENAI_API_KEY is not set. Set environment variable and restart server.", "raw_text": raw_text}

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",   # change model if you prefer
            messages=[{"role":"user","content": prompt}],
            temperature=0
        )
        llm_text = resp.choices[0].message["content"]
    except Exception as e:
        return {"error": "OpenAI API call failed", "details": str(e), "raw_text": raw_text}

    # 4) Try to extract JSON from the LLM response
    parsed = None
    try:
        parsed = json.loads(llm_text)
    except Exception:
        # Try to find the first {...} block and parse that
        m = re.search(r'(\{[\s\S]*\})', llm_text)
        if m:
            possible = m.group(1)
            try:
                parsed = json.loads(possible)
            except Exception:
                parsed = {"raw_llm_output": llm_text}
        else:
            parsed = {"raw_llm_output": llm_text}

    return {
        "raw_text": raw_text,
        "dpp_json": parsed
    }
>>>>>>> 43c042e6d4fb2e094d29fa30ddf6ce41c063f7fe
