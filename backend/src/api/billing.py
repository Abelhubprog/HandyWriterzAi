import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..services.security_service import get_current_user
from ..services.payment_service import payment_service, SubscriptionTier, PaymentProvider
from ..db.database import get_db
from ..db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()

class BillingSummary(BaseModel):
    plan: str
    renew_date: str
    usage_usd: float
    credits_remaining: int
    max_words: int
    features: List[str]

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

class SubscriptionUpgradeRequest(BaseModel):
    tier: str = Field(..., description="Target subscription tier")
    provider: str = Field(..., description="Payment provider (paystack or coinbase_commerce)")
    metadata: Optional[Dict[str, Any]] = None

@router.get("/billing/summary", response_model=BillingSummary)
async def get_billing_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing summary for the current user."""
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get tier configuration
    tier_config = payment_service.get_pricing_tiers().get(user.subscription_tier, {})
    
    # Calculate next renewal date (30 days from last update for paid plans)
    renew_date = "N/A"
    if user.subscription_tier != "free" and user.updated_at:
        next_renewal = user.updated_at + timedelta(days=30)
        renew_date = next_renewal.strftime("%Y-%m-%d")
    
    # Mock usage calculation - in production, sum from usage logs
    usage_usd = max(0, (tier_config.get("credits", 0) - user.credits_remaining) * 0.05)
    
    return BillingSummary(
        plan=user.subscription_tier,
        renew_date=renew_date,
        usage_usd=usage_usd,
        credits_remaining=user.credits_remaining,
        max_words=tier_config.get("max_words", 1000),
        features=tier_config.get("features", [])
    )

@router.get("/billing/methods", response_model=List[PaymentMethod])
async def list_payment_methods(current_user: dict = Depends(get_current_user)):
    """List payment methods for the current user."""
    # In production, this would query saved payment methods from DB
    # For now, return available payment options
    return [
        PaymentMethod(id="paystack_card", brand="Paystack", last4="Card", type="fiat"),
        PaymentMethod(id="coinbase_crypto", brand="Coinbase", last4="USDC", type="crypto")
    ]

@router.post("/billing/upgrade")
async def upgrade_subscription(
    upgrade_request: SubscriptionUpgradeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create payment link to upgrade subscription."""
    try:
        # Validate tier
        try:
            tier = SubscriptionTier(upgrade_request.tier)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        # Validate provider
        try:
            provider = PaymentProvider(upgrade_request.provider)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payment provider")
        
        user_id = current_user["id"]
        
        # Check if user is already on this tier or higher
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.subscription_tier == tier.value:
            raise HTTPException(status_code=400, detail="Already on this subscription tier")
        
        # Create payment based on provider
        if provider == PaymentProvider.PAYSTACK:
            payment_data = await payment_service.create_paystack_payment_link(
                user_id=user_id,
                tier=tier,
                metadata=upgrade_request.metadata
            )
        elif provider == PaymentProvider.COINBASE_COMMERCE:
            payment_data = await payment_service.create_coinbase_charge(
                user_id=user_id,
                tier=tier,
                metadata=upgrade_request.metadata
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment provider")
        
        logger.info(f"Created subscription upgrade for user {user_id}, tier {tier.value}, provider {provider.value}")
        
        return {
            "success": True,
            "payment_data": payment_data,
            "message": f"Payment link created for {tier.value} subscription upgrade"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create subscription upgrade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/billing/tiers")
async def get_available_tiers():
    """Get all available subscription tiers."""
    return {
        "tiers": payment_service.get_pricing_tiers(),
        "providers": [provider.value for provider in PaymentProvider]
    }

@router.post("/billing/verify-payment")
async def verify_subscription_payment(
    reference: str,
    provider: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify payment and activate subscription."""
    try:
        # Validate provider
        try:
            payment_provider = PaymentProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payment provider")
        
        user_id = current_user["id"]
        
        # Verify payment based on provider
        if payment_provider == PaymentProvider.PAYSTACK:
            verification_result = await payment_service.verify_paystack_payment(reference)
        elif payment_provider == PaymentProvider.COINBASE_COMMERCE:
            verification_result = await payment_service.verify_coinbase_payment(reference)
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment provider")
        
        if verification_result["status"] != "success":
            return {
                "success": False,
                "message": "Payment verification failed or pending",
                "status": verification_result["status"]
            }
        
        # Extract tier from metadata
        metadata = verification_result.get("metadata", {})
        tier_str = metadata.get("tier")
        
        if not tier_str:
            raise HTTPException(status_code=400, detail="Tier information missing from payment")
        
        try:
            tier = SubscriptionTier(tier_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tier in payment metadata")
        
        # Upgrade user subscription
        success = await payment_service.upgrade_user_subscription(
            db=db,
            user_id=user_id,
            tier=tier,
            payment_data=verification_result
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to activate subscription")
        
        logger.info(f"Subscription activated for user {user_id} - tier: {tier.value}")
        
        return {
            "success": True,
            "message": "Payment verified and subscription activated successfully",
            "tier": tier.value,
            "verification_data": verification_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify subscription payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/billing/methods")
async def add_payment_method(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Add a new payment method (Paystack or Coinbase)."""
    # This would store payment method preferences in production
    logger.info(f"Adding payment method for user {current_user.get('id')}: {payload}")
    return {"status": "success", "message": "Payment method preference saved."}

@router.get("/billing/invoices", response_model=List[Invoice])
async def list_invoices(current_user: dict = Depends(get_current_user)):
    """List past invoices for the current user."""
    # In production, this would query payment history from DB
    return [
        Invoice(id="in_123", pdf_url="/invoices/in_123.pdf", total=19.99, date="2025-01-17"),
        Invoice(id="in_456", pdf_url="/invoices/in_456.pdf", total=19.99, date="2024-12-17")
    ]

@router.get("/billing/usage")
async def get_usage_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage statistics."""
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tier_config = payment_service.get_pricing_tiers().get(user.subscription_tier, {})
    
    return {
        "subscription_tier": user.subscription_tier,
        "credits_remaining": user.credits_remaining,
        "total_credits": tier_config.get("credits", 0),
        "documents_created": user.total_documents_created,
        "words_written": user.total_words_written,
        "average_quality": user.average_quality_score,
        "max_words_per_doc": tier_config.get("max_words", 1000),
        "features": tier_config.get("features", [])
    }
