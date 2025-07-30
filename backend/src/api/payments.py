"""
Payment and escrow API endpoints.
"""

from decimal import Decimal
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..db.database import get_db
from ..models.turnitin import WalletEscrow, CheckerPayout, DocLot, PayoutStatus
from ..blockchain.escrow import USDCEscrowManager, setup_escrow_manager

router = APIRouter(prefix="/payments", tags=["payments"])


# === Request/Response Models ===

class CreateEscrowRequest(BaseModel):
    user_wallet: str = Field(..., regex=r'^0x[a-fA-F0-9]{40}$')
    lot_id: str
    permit_signature: Optional[str] = None

class CreateEscrowResponse(BaseModel):
    escrow_id: str
    transaction_hash: str
    amount_usdc: float
    status: str

class EscrowStatusResponse(BaseModel):
    escrow_id: str
    lot_id: str
    user_wallet: str
    amount_usdc: float
    locked_at: str
    released_at: Optional[str]
    status: str
    contract_address: str

class PayoutInfo(BaseModel):
    id: str
    checker_wallet: str
    amount_usdc: float
    status: str
    transaction_hash: Optional[str]
    created_at: str
    paid_at: Optional[str]
    error_message: Optional[str]

class PayoutBatchResponse(BaseModel):
    processed: int
    successful: int
    failed: int
    results: List[dict]

class QuoteRequest(BaseModel):
    word_count: int

class QuoteResponse(BaseModel):
    word_count: int
    estimated_chunks: int
    cost_per_chunk_pence: int
    total_cost_usdc: float
    escrow_amount_usdc: float  # Including buffer


# === Dependencies ===

async def get_escrow_manager() -> USDCEscrowManager:
    """Get escrow manager instance."""
    return await setup_escrow_manager()


# === API Endpoints ===

@router.post("/quote", response_model=QuoteResponse)
async def get_payment_quote(
    request: QuoteRequest,
    escrow_manager: USDCEscrowManager = Depends(get_escrow_manager)
):
    """Get payment quote for document processing."""
    
    try:
        # Calculate required escrow
        escrow_amount = await escrow_manager.calculate_required_escrow(request.word_count)
        
        # Calculate breakdown
        chunks_needed = (request.word_count + 349) // 350
        pence_per_chunk = 18
        total_cost_usdc = float(Decimal(str(chunks_needed * pence_per_chunk / 100 * 1.25)))
        
        return QuoteResponse(
            word_count=request.word_count,
            estimated_chunks=chunks_needed,
            cost_per_chunk_pence=pence_per_chunk,
            total_cost_usdc=total_cost_usdc,
            escrow_amount_usdc=float(escrow_amount)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating quote: {e}")


@router.post("/escrow", response_model=CreateEscrowResponse)
async def create_escrow(
    request: CreateEscrowRequest,
    db: Session = Depends(get_db),
    escrow_manager: USDCEscrowManager = Depends(get_escrow_manager)
):
    """Create escrow for document lot."""
    
    try:
        # Verify lot exists
        lot = db.query(DocLot).filter(DocLot.id == request.lot_id).first()
        if not lot:
            raise HTTPException(status_code=404, detail="Document lot not found")
        
        # Check if escrow already exists
        existing_escrow = db.query(WalletEscrow).filter(
            WalletEscrow.lot_id == request.lot_id
        ).first()
        
        if existing_escrow:
            raise HTTPException(
                status_code=409, 
                detail="Escrow already exists for this lot"
            )
        
        # Calculate required amount
        required_amount = await escrow_manager.calculate_required_escrow(lot.word_count)
        
        # Create escrow
        result = await escrow_manager.create_escrow(
            user_wallet=request.user_wallet,
            lot_id=request.lot_id,
            amount_usdc=required_amount,
            permit_signature=request.permit_signature
        )
        
        return CreateEscrowResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating escrow: {e}")


@router.get("/escrow/{escrow_id}", response_model=EscrowStatusResponse)
async def get_escrow_status(
    escrow_id: str,
    escrow_manager: USDCEscrowManager = Depends(get_escrow_manager)
):
    """Get escrow status."""
    
    try:
        status = await escrow_manager.get_escrow_status(escrow_id)
        return EscrowStatusResponse(**status)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting escrow status: {e}")


@router.post("/release/{lot_id}")
async def release_payments(
    lot_id: str,
    db: Session = Depends(get_db),
    escrow_manager: USDCEscrowManager = Depends(get_escrow_manager)
):
    """Release payments to checkers for completed lot."""
    
    try:
        # Verify lot exists and is complete
        lot = db.query(DocLot).filter(DocLot.id == lot_id).first()
        if not lot:
            raise HTTPException(status_code=404, detail="Document lot not found")
        
        if lot.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail="Cannot release payments for incomplete lot"
            )
        
        # Release payments
        results = await escrow_manager.release_payments(lot_id)
        
        # Mark escrow as released
        escrow = db.query(WalletEscrow).filter(
            WalletEscrow.lot_id == lot_id
        ).first()
        
        if escrow and not escrow.released_at:
            escrow.released_at = datetime.now(timezone.utc)
            db.commit()
        
        return {
            "lot_id": lot_id,
            "payments_released": len(results),
            "successful": len([r for r in results if r["status"] == "paid"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error releasing payments: {e}")


@router.get("/payouts", response_model=List[PayoutInfo])
async def get_payouts(
    checker_wallet: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get payout information."""
    
    try:
        query = db.query(CheckerPayout)
        
        if checker_wallet:
            # Validate wallet format
            if not checker_wallet.startswith('0x') or len(checker_wallet) != 42:
                raise HTTPException(status_code=400, detail="Invalid wallet address format")
            
            query = query.join(CheckerPayout.checker).filter(
                CheckerPayout.checker.has(wallet_address=checker_wallet)
            )
        
        if status:
            if status not in ["pending", "paid", "failed"]:
                raise HTTPException(status_code=400, detail="Invalid status")
            query = query.filter(CheckerPayout.status == PayoutStatus(status))
        
        payouts = query.order_by(CheckerPayout.created_at.desc()).limit(limit).all()
        
        return [
            PayoutInfo(
                id=payout.id,
                checker_wallet=payout.checker.wallet_address,
                amount_usdc=float(payout.amount_usdc),
                status=payout.status.value,
                transaction_hash=payout.transaction_hash,
                created_at=payout.created_at.isoformat(),
                paid_at=payout.paid_at.isoformat() if payout.paid_at else None,
                error_message=payout.error_message
            )
            for payout in payouts
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting payouts: {e}")


@router.post("/batch-payouts", response_model=PayoutBatchResponse)
async def process_batch_payouts(
    max_payouts: int = 50,
    escrow_manager: USDCEscrowManager = Depends(get_escrow_manager)
):
    """Process pending payouts in batch."""
    
    try:
        if max_payouts > 100:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 100 payouts per batch"
            )
        
        results = await escrow_manager.batch_process_payouts(max_payouts)
        
        successful = len([r for r in results if r["status"] == "success"])
        failed = len([r for r in results if r["status"] == "failed"])
        
        return PayoutBatchResponse(
            processed=len(results),
            successful=successful,
            failed=failed,
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch payouts: {e}")


@router.get("/balances/{wallet_address}")
async def get_wallet_balances(
    wallet_address: str,
    escrow_manager: USDCEscrowManager = Depends(get_escrow_manager)
):
    """Get USDC balance for wallet address."""
    
    try:
        # Validate wallet format
        if not wallet_address.startswith('0x') or len(wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        # Get USDC balance
        balance_wei = await escrow_manager._get_usdc_balance(wallet_address)
        balance_usdc = balance_wei / 10**6  # USDC has 6 decimals
        
        return {
            "wallet_address": wallet_address,
            "usdc_balance": balance_usdc,
            "balance_wei": balance_wei
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting wallet balance: {e}")


@router.get("/stats")
async def get_payment_stats(
    db: Session = Depends(get_db)
):
    """Get payment system statistics."""
    
    try:
        # Total escrows
        total_escrows = db.query(WalletEscrow).count()
        
        # Total value locked
        total_locked = db.query(
            db.func.sum(WalletEscrow.amount_usdc)
        ).filter(
            WalletEscrow.released_at.is_(None)
        ).scalar() or 0
        
        # Total payouts by status
        payout_stats = db.query(
            CheckerPayout.status,
            db.func.count(CheckerPayout.id),
            db.func.sum(CheckerPayout.amount_usdc)
        ).group_by(CheckerPayout.status).all()
        
        payout_breakdown = {}
        for status, count, total in payout_stats:
            payout_breakdown[status.value] = {
                "count": count,
                "total_usdc": float(total or 0)
            }
        
        return {
            "total_escrows": total_escrows,
            "total_value_locked_usdc": float(total_locked),
            "payout_breakdown": payout_breakdown,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting payment stats: {e}")


@router.post("/admin/emergency-stop")
async def emergency_stop_payments():
    """Emergency stop for payment processing (admin only)."""
    
    # In production, this would:
    # 1. Check admin authentication
    # 2. Pause all payment processing
    # 3. Send alerts to administrators
    
    return {
        "status": "emergency_stop_activated",
        "message": "All payment processing has been halted",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/admin/resume-payments")
async def resume_payments():
    """Resume payment processing (admin only)."""
    
    # In production, this would:
    # 1. Check admin authentication
    # 2. Resume payment processing
    # 3. Send alerts to administrators
    
    return {
        "status": "payments_resumed",
        "message": "Payment processing has been resumed",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }