import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..services.security_service import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

class BillingSummary(BaseModel):
    plan: str
    renew_date: str
    usage_usd: float

class PaymentMethod(BaseModel):
    id: str
    brand: str
    last4: str
    type: str

class Invoice(BaseModel):
    id: str
    pdf_url: str
    total: float
    date: str

@router.get("/billing/summary", response_model=BillingSummary)
async def get_billing_summary(current_user: dict = Depends(get_current_user)):
    """Get billing summary for the current user."""
    # Placeholder implementation
    return BillingSummary(
        plan="pro",
        renew_date="2025-08-17",
        usage_usd=42.50
    )

@router.get("/billing/methods", response_model=List[PaymentMethod])
async def list_payment_methods(current_user: dict = Depends(get_current_user)):
    """List payment methods for the current user."""
    # Placeholder implementation
    return [
        PaymentMethod(id="pm_123", brand="Visa", last4="4242", type="card"),
        PaymentMethod(id="cw_456", brand="USDC", last4="a1b2", type="crypto")
    ]

@router.post("/billing/methods")
async def add_payment_method(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Add a new payment method (Stripe or Coinbase)."""
    # Placeholder implementation
    logger.info(f"Adding payment method for user {current_user.get('id')}: {payload}")
    return {"status": "success", "message": "Payment method added."}

@router.get("/billing/invoices", response_model=List[Invoice])
async def list_invoices(current_user: dict = Depends(get_current_user)):
    """List past invoices for the current user."""
    # Placeholder implementation
    return [
        Invoice(id="in_123", pdf_url="/invoices/in_123.pdf", total=50.00, date="2025-07-17"),
        Invoice(id="in_456", pdf_url="/invoices/in_456.pdf", total=50.00, date="2025-06-17")
    ]
