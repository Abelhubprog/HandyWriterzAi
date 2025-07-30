"""Payment service integrating Paystack and Coinbase Commerce for HandyWriterz."""

import os
import json
import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from enum import Enum

from ..db.models import User
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class PaymentProvider(Enum):
    PAYSTACK = "paystack"
    COINBASE_COMMERCE = "coinbase_commerce"

class SubscriptionTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

# Pricing tiers configuration
PRICING_TIERS = {
    SubscriptionTier.FREE: {
        "price_usd": 0,
        "credits": 3,
        "features": ["3 documents", "Basic templates", "Community support"],
        "max_words": 1000,
        "paystack_plan_code": None,
        "coinbase_product_id": None
    },
    SubscriptionTier.BASIC: {
        "price_usd": 19.99,
        "credits": 50,
        "features": ["50 documents", "Advanced templates", "Email support", "Export to PDF/DOCX"],
        "max_words": 5000,
        "paystack_plan_code": "PLN_basic_monthly",
        "coinbase_product_id": "basic-monthly"
    },
    SubscriptionTier.PRO: {
        "price_usd": 49.99,
        "credits": 200,
        "features": ["200 documents", "All templates", "Priority support", "Advanced AI models", "Plagiarism check"],
        "max_words": 15000,
        "paystack_plan_code": "PLN_pro_monthly",
        "coinbase_product_id": "pro-monthly"
    },
    SubscriptionTier.ENTERPRISE: {
        "price_usd": 199.99,
        "credits": 1000,
        "features": ["Unlimited documents", "Custom templates", "24/7 support", "Team collaboration", "API access"],
        "max_words": 50000,
        "paystack_plan_code": "PLN_enterprise_monthly",
        "coinbase_product_id": "enterprise-monthly"
    }
}

class PaymentService:
    """Service for handling payments through Paystack and Coinbase Commerce."""
    
    def __init__(self):
        self.paystack_secret_key = settings.paystack_secret_key
        self.coinbase_api_key = settings.coinbase_api_key
        self.coinbase_webhook_secret = settings.coinbase_webhook_secret
        
        self.paystack_base_url = "https://api.paystack.co"
        self.coinbase_base_url = "https://api.commerce.coinbase.com"
    
    async def create_paystack_payment_link(
        self, 
        user_id: str, 
        tier: SubscriptionTier,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment link for Paystack subscription."""
        if not self.paystack_secret_key:
            raise ValueError("Paystack secret key not configured")
        
        tier_config = PRICING_TIERS[tier]
        if not tier_config["paystack_plan_code"]:
            raise ValueError(f"No Paystack plan configured for tier {tier.value}")
        
        headers = {
            "Authorization": f"Bearer {self.paystack_secret_key}",
            "Content-Type": "application/json"
        }
        
        # Create customer first
        customer_data = {
            "email": f"user-{user_id}@handywriterz.ai",
            "first_name": "User",
            "last_name": str(user_id)[:8],
        }
        
        async with httpx.AsyncClient() as client:
            # Create or get customer
            customer_response = await client.post(
                f"{self.paystack_base_url}/customer",
                headers=headers,
                json=customer_data
            )
            
            if customer_response.status_code != 200:
                logger.error(f"Failed to create Paystack customer: {customer_response.text}")
                raise Exception("Failed to create customer")
            
            customer = customer_response.json()["data"]
            
            # Create subscription
            subscription_data = {
                "customer": customer["customer_code"],
                "plan": tier_config["paystack_plan_code"],
                "metadata": {
                    "user_id": user_id,
                    "tier": tier.value,
                    **(metadata or {})
                }
            }
            
            subscription_response = await client.post(
                f"{self.paystack_base_url}/subscription",
                headers=headers,
                json=subscription_data
            )
            
            if subscription_response.status_code != 200:
                logger.error(f"Failed to create Paystack subscription: {subscription_response.text}")
                raise Exception("Failed to create subscription")
            
            subscription = subscription_response.json()["data"]
            
            return {
                "provider": PaymentProvider.PAYSTACK.value,
                "payment_url": subscription["authorization_url"],
                "subscription_code": subscription["subscription_code"],
                "customer_code": customer["customer_code"],
                "amount": tier_config["price_usd"] * 100,  # Paystack uses kobo
                "tier": tier.value
            }
    
    async def create_coinbase_charge(
        self, 
        user_id: str, 
        tier: SubscriptionTier,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a crypto charge using Coinbase Commerce."""
        if not self.coinbase_api_key:
            raise ValueError("Coinbase API key not configured")
        
        tier_config = PRICING_TIERS[tier]
        
        headers = {
            "Content-Type": "application/json",
            "X-CC-Api-Key": self.coinbase_api_key,
            "X-CC-Version": "2018-03-22"
        }
        
        charge_data = {
            "name": f"HandyWriterz {tier.value.title()} Subscription",
            "description": f"Monthly subscription to HandyWriterz {tier.value.title()} plan",
            "pricing_type": "fixed_price",
            "local_price": {
                "amount": str(tier_config["price_usd"]),
                "currency": "USD"
            },
            "metadata": {
                "user_id": user_id,
                "tier": tier.value,
                "subscription_type": "monthly",
                **(metadata or {})
            },
            "redirect_url": f"{settings.frontend_url}/payment/success",
            "cancel_url": f"{settings.frontend_url}/payment/cancel"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.coinbase_base_url}/charges",
                headers=headers,
                json=charge_data
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create Coinbase charge: {response.text}")
                raise Exception("Failed to create crypto payment")
            
            charge = response.json()["data"]
            
            return {
                "provider": PaymentProvider.COINBASE_COMMERCE.value,
                "payment_url": charge["hosted_url"],
                "charge_id": charge["id"],
                "charge_code": charge["code"],
                "amount_usd": tier_config["price_usd"],
                "tier": tier.value,
                "expires_at": charge["expires_at"]
            }
    
    async def verify_paystack_payment(self, reference: str) -> Dict[str, Any]:
        """Verify a Paystack payment."""
        if not self.paystack_secret_key:
            raise ValueError("Paystack secret key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.paystack_secret_key}",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.paystack_base_url}/transaction/verify/{reference}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to verify Paystack payment: {response.text}")
                return {"status": "failed", "message": "Verification failed"}
            
            data = response.json()["data"]
            
            return {
                "status": "success" if data["status"] == "success" else "failed",
                "amount": data["amount"] / 100,  # Convert from kobo
                "currency": data["currency"],
                "customer_email": data["customer"]["email"],
                "metadata": data["metadata"],
                "paid_at": data["paid_at"],
                "reference": data["reference"]
            }
    
    async def verify_coinbase_payment(self, charge_id: str) -> Dict[str, Any]:
        """Verify a Coinbase Commerce payment."""
        if not self.coinbase_api_key:
            raise ValueError("Coinbase API key not configured")
        
        headers = {
            "X-CC-Api-Key": self.coinbase_api_key,
            "X-CC-Version": "2018-03-22"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.coinbase_base_url}/charges/{charge_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to verify Coinbase payment: {response.text}")
                return {"status": "failed", "message": "Verification failed"}
            
            charge = response.json()["data"]
            
            # Check if payment is confirmed
            is_paid = any(
                timeline["status"] == "CONFIRMED" 
                for timeline in charge.get("timeline", [])
            )
            
            return {
                "status": "success" if is_paid else "pending",
                "amount": float(charge["pricing"]["local"]["amount"]),
                "currency": charge["pricing"]["local"]["currency"],
                "metadata": charge["metadata"],
                "confirmed_at": charge.get("confirmed_at"),
                "charge_id": charge["id"]
            }
    
    async def upgrade_user_subscription(
        self, 
        db: Session, 
        user_id: str, 
        tier: SubscriptionTier,
        payment_data: Dict[str, Any]
    ) -> bool:
        """Upgrade user's subscription tier and credits."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return False
            
            tier_config = PRICING_TIERS[tier]
            
            # Update user subscription
            user.subscription_tier = tier.value
            user.credits_remaining = tier_config["credits"]
            user.updated_at = datetime.utcnow()
            
            # Set subscription renewal date (30 days from now)
            # You might want to store this in a separate subscriptions table
            
            db.commit()
            
            logger.info(f"User {user_id} upgraded to {tier.value} tier")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upgrade user subscription: {e}")
            db.rollback()
            return False
    
    def get_pricing_tiers(self) -> Dict[str, Any]:
        """Get all available pricing tiers."""
        return {
            tier.value: {
                "name": tier.value.title(),
                "price_usd": config["price_usd"],
                "credits": config["credits"],
                "features": config["features"],
                "max_words": config["max_words"]
            }
            for tier, config in PRICING_TIERS.items()
        }
    
    def can_user_afford_request(self, user: User, estimated_cost: float) -> bool:
        """Check if user has enough credits for a request."""
        tier_config = PRICING_TIERS.get(SubscriptionTier(user.subscription_tier), PRICING_TIERS[SubscriptionTier.FREE])
        
        # Simple credit check - you might want more sophisticated cost calculation
        return user.credits_remaining > 0
    
    def deduct_credits(self, db: Session, user: User, cost: float = 1) -> bool:
        """Deduct credits from user account."""
        if user.credits_remaining >= cost:
            user.credits_remaining -= cost
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

# Global payment service instance
payment_service = PaymentService()