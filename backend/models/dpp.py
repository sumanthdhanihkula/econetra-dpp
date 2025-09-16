from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Supplier(BaseModel):
    name: str
    address: Optional[str] = None
    contact: Optional[str] = None

class InvoiceDetails(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    currency: Optional[str] = "INR"

class DPP(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    material_composition: Optional[str] = None
    batch_number: Optional[str] = None
    supplier: Optional[Supplier] = None
    manufacture_date: Optional[str] = None
    expiry_date: Optional[str] = None
    certifications: Optional[List[str]] = []
    sustainability_score: Optional[float] = None
    invoice_details: Optional[InvoiceDetails] = None
    traceability: Optional[Dict[str, str]] = None
    compliance_status: Optional[str] = "pending"
