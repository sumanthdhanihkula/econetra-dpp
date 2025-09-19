# backend/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from bson.objectid import ObjectId

import pytesseract
from PIL import Image
import io
import os
import json
import openai
import re
import uuid
import boto3  # for AWS S3

# Import MongoDB connection + model
from database import db
from models.dpp import DPP

# ----------------------------
# AWS S3 Config
# ----------------------------
S3_BUCKET = "econetra-dpp-uploads"
S3_REGION = "ap-south-1"
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3 = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

# ----------------------------
# FastAPI Init
# ----------------------------
app = FastAPI(title="Econetra DPP API")

# --- CORS for frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for now
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files (local fallback if needed) ---
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ----------------------------
# Health / Root
# ----------------------------
@app.get("/status")
async def get_status():
    return {"status": "OK"}

@app.get("/")
async def root():
    return {"message": "Econetra DPP API up"}

# ----------------------------
# DPP CRUD
# ----------------------------
@app.post("/dpp", status_code=201)
async def create_dpp(dpp: DPP):
    doc = dpp.dict()
    result = await db.dpps.insert_one(doc)
    return {"id": str(result.inserted_id)}

@app.get("/dpp")
async def list_dpps(limit: int = 50):
    cursor = db.dpps.find().sort([("_id", -1)]).limit(limit)   # ✅ fixed brackets
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return items

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

# ----------------------------
# Upload Image (to AWS S3)
# ----------------------------
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    if not S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3 bucket not configured")

    try:
        key = f"dpps/{uuid.uuid4().hex}_{file.filename}"
        file.file.seek(0)

        s3.upload_fileobj(
            file.file,
            S3_BUCKET,
            key,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
        )

        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ----------------------------
# OCR + AI
# ----------------------------
# On Linux EC2, pytesseract is usually installed globally
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# Schema prompt
DPP_SCHEMA_PROMPT = """
You are an assistant that converts messy invoice text into a JSON matching the DPP schema below.
Return only VALID JSON and nothing else.

Schema:
{{
  "product_id": "string or null",
  "product_name": "string or null",
  "category": "string or null",
  "material_composition": "string or null",
  "batch_number": "string or null",
  "supplier": {{
    "name": "string or null",
    "address": "string or null",
    "contact": "string or null"
  }},
  "manufacture_date": "string (YYYY-MM-DD) or null",
  "expiry_date": "string (YYYY-MM-DD) or null",
  "certifications": ["string", "..."] or [],
  "sustainability_score": "string or null",
  "invoice_details": {{
    "invoice_number": "string or null",
    "invoice_date": "string or null",
    "quantity": integer or null,
    "price": float or null,
    "currency": "string or null"
  }},
  "traceability": {{
    "origin_country": "string or null",
    "factory_location": "string or null",
    "transport_mode": "string or null"
  }}
}}

If a field cannot be found, set it to null (or [] for lists).
Invoice text:
{raw_text}
"""

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        return {"error": "Invalid image", "details": str(e)}

    raw_text = pytesseract.image_to_string(image)
    prompt = DPP_SCHEMA_PROMPT.format(raw_text=raw_text)

    if not openai.api_key:
        return {"error": "OPENAI_API_KEY not set", "raw_text": raw_text}

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        llm_text = resp.choices[0].message["content"]
    except Exception as e:
        return {"error": "OpenAI API call failed", "details": str(e), "raw_text": raw_text}

    try:
        parsed = json.loads(llm_text)
    except Exception:
        m = re.search(r'(\{[\s\S]*\})', llm_text)
        parsed = json.loads(m.group(1)) if m else {"raw_llm_output": llm_text}

    return {"raw_text": raw_text, "dpp_json": parsed}
