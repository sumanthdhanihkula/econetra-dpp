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
