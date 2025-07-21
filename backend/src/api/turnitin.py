"""
FastAPI endpoints for Turnitin Checker workflow.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..db.database import get_db
from ..models.turnitin import (
    DocChunk, Checker, Submission, CheckerPayout, ChunkStatus, PayoutStatus, CheckerStatus
)

router = APIRouter(prefix="/checker", tags=["turnitin"])


# === Request/Response Models ===

from pydantic import BaseModel, Field

class ChunkClaimRequest(BaseModel):
    chunk_id: str

class ChunkClaimResponse(BaseModel):
    file_url: str
    bounty: float
    claimed_at: datetime
    timeout_minutes: int = 15

class ChunkSubmitRequest(BaseModel):
    chunk_id: str
    similarity_score: float = Field(ge=0, le=100)
    ai_score: float = Field(ge=0, le=100)
    flagged_text: List[str]
    checker_notes: Optional[str] = None

class ChunkSubmitResponse(BaseModel):
    success: bool
    submission_id: str
    needs_rewrite: bool

class ChunkInfo(BaseModel):
    id: str
    chunk_number: int
    word_count: int
    status: str
    bounty: float = 0.18  # £0.18 default
    created_at: datetime

class CheckerEarnings(BaseModel):
    total_usdc: Decimal
    pending_payouts: int
    completed_chunks: int
    average_rating: Optional[float]


# === Helper Functions ===

def get_current_checker(wallet_address: str, db: Session) -> Checker:
    """Get checker by wallet address or raise 404."""
    checker = db.query(Checker).filter(
        Checker.wallet_address == wallet_address
    ).first()
    if not checker:
        raise HTTPException(status_code=404, detail="Checker not found")
    if checker.status != CheckerStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Checker account suspended")
    return checker

def calculate_payout_amount(word_count: int) -> tuple[int, Decimal]:
    """Calculate payout in pence and USDC for a chunk."""
    # Base rate: 18 pence per chunk
    pence_amount = 18
    # Convert to USDC (simplified rate: 1 GBP = 1.25 USD)
    usdc_amount = Decimal(str(pence_amount / 100 * 1.25))
    return pence_amount, usdc_amount

def cleanup_expired_claims(db: Session) -> int:
    """Release expired chunk claims and return count."""
    expired_chunks = db.query(DocChunk).filter(
        and_(
            DocChunk.status == ChunkStatus.CHECKING,
            DocChunk.claimed_at.isnot(None),
            func.extract('epoch', func.now() - DocChunk.claimed_at) > 900  # 15 minutes
        )
    ).all()
    
    count = 0
    for chunk in expired_chunks:
        if chunk.unclaim_if_timeout():
            count += 1
    
    db.commit()
    return count


# === API Endpoints ===

@router.post("/claim", response_model=ChunkClaimResponse)
async def claim_chunk(
    request: ChunkClaimRequest,
    wallet_address: str,
    db: Session = Depends(get_db)
):
    """Claim a chunk for checking (15-minute timeout)."""
    
    # Clean up expired claims first
    cleanup_expired_claims(db)
    
    # Verify checker exists and is active
    checker = get_current_checker(wallet_address, db)
    
    # Check if checker can claim more chunks (max 3)
    active_claims = db.query(DocChunk).filter(
        and_(
            DocChunk.claimed_by == wallet_address,
            DocChunk.status == ChunkStatus.CHECKING
        )
    ).count()
    
    if active_claims >= 3:
        raise HTTPException(
            status_code=429, 
            detail="Maximum 3 active claims allowed"
        )
    
    # Find and claim the chunk
    chunk = db.query(DocChunk).filter(
        and_(
            DocChunk.id == request.chunk_id,
            DocChunk.status == ChunkStatus.OPEN
        )
    ).first()
    
    if not chunk:
        raise HTTPException(
            status_code=404, 
            detail="Chunk not available for claiming"
        )
    
    # Claim the chunk
    chunk.status = ChunkStatus.CHECKING
    chunk.claimed_by = wallet_address
    chunk.claimed_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Generate file URL (simplified - would use S3/R2 in production)
    file_url = f"/api/files/chunks/{chunk.id}/content.docx"
    
    return ChunkClaimResponse(
        file_url=file_url,
        bounty=0.18,
        claimed_at=chunk.claimed_at,
        timeout_minutes=15
    )


@router.post("/submit", response_model=ChunkSubmitResponse)
async def submit_chunk(
    chunk_id: str = Form(...),
    similarity_score: float = Form(...),
    ai_score: float = Form(...),
    flagged_text: str = Form(...),  # JSON string
    checker_notes: Optional[str] = Form(None),
    similarity_pdf: UploadFile = File(...),
    ai_pdf: UploadFile = File(...),
    wallet_address: str = Form(...),
    db: Session = Depends(get_db)
):
    """Submit Turnitin PDFs and flagged text for a chunk."""
    
    import json
    
    # Parse flagged_text JSON
    try:
        flagged_list = json.loads(flagged_text)
        if not isinstance(flagged_list, list):
            raise ValueError()
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=400, 
            detail="flagged_text must be valid JSON array"
        )
    
    # Verify checker and chunk ownership
    checker = get_current_checker(wallet_address, db)
    
    chunk = db.query(DocChunk).filter(
        and_(
            DocChunk.id == chunk_id,
            DocChunk.claimed_by == wallet_address,
            DocChunk.status == ChunkStatus.CHECKING
        )
    ).first()
    
    if not chunk:
        raise HTTPException(
            status_code=404, 
            detail="Chunk not found or not claimed by you"
        )
    
    # Validate file uploads
    if not similarity_pdf.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="similarity_pdf must be PDF")
    if not ai_pdf.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="ai_pdf must be PDF")
    
    # Save files (simplified - would use S3/R2 in production)
    sim_pdf_url = f"/api/files/submissions/{chunk_id}_sim_{uuid.uuid4().hex[:8]}.pdf"
    ai_pdf_url = f"/api/files/submissions/{chunk_id}_ai_{uuid.uuid4().hex[:8]}.pdf"
    
    # Create submission record
    submission = Submission(
        chunk_id=chunk_id,
        checker_id=checker.id,
        similarity_pdf_url=sim_pdf_url,
        ai_pdf_url=ai_pdf_url,
        similarity_score=similarity_score,
        ai_score=ai_score,
        flagged_text=flagged_list,
        checker_notes=checker_notes
    )
    
    db.add(submission)
    
    # Update chunk status based on scores
    needs_rewrite = submission.needs_rewrite
    
    if needs_rewrite:
        chunk.status = ChunkStatus.NEEDS_EDIT
    else:
        chunk.status = ChunkStatus.DONE
        chunk.completed_at = datetime.now(timezone.utc)
        
        # Create payout record
        pence_amount, usdc_amount = calculate_payout_amount(chunk.word_count)
        
        payout = CheckerPayout(
            checker_id=checker.id,
            chunk_id=chunk_id,
            amount_pence=pence_amount,
            amount_usdc=usdc_amount
        )
        db.add(payout)
        
        # Update checker stats
        checker.chunks_completed += 1
        checker.total_earnings += usdc_amount
        checker.last_active = datetime.now(timezone.utc)
    
    # Clear claim regardless
    chunk.claimed_by = None
    chunk.claimed_at = None
    
    # Update chunk scores
    chunk.turnitin_sim_score = similarity_score
    chunk.turnitin_ai_score = ai_score
    chunk.flagged_spans = flagged_list
    
    db.commit()
    
    return ChunkSubmitResponse(
        success=True,
        submission_id=submission.id,
        needs_rewrite=needs_rewrite
    )


@router.get("/chunks", response_model=List[ChunkInfo])
async def get_available_chunks(
    status: Optional[str] = "open",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of chunks available for claiming."""
    
    # Clean up expired claims first
    cleanup_expired_claims(db)
    
    # Build query
    query = db.query(DocChunk)
    
    if status:
        if status not in ["open", "checking", "needs_edit", "done"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        query = query.filter(DocChunk.status == ChunkStatus(status))
    
    chunks = query.order_by(DocChunk.created_at.desc()).limit(limit).all()
    
    return [
        ChunkInfo(
            id=chunk.id,
            chunk_number=chunk.chunk_number,
            word_count=chunk.word_count,
            status=chunk.status.value,
            created_at=chunk.created_at
        )
        for chunk in chunks
    ]


@router.get("/earnings", response_model=CheckerEarnings)
async def get_checker_earnings(
    wallet_address: str,
    db: Session = Depends(get_db)
):
    """Get checker's earnings and statistics."""
    
    checker = get_current_checker(wallet_address, db)
    
    # Count pending payouts
    pending_payouts = db.query(CheckerPayout).filter(
        and_(
            CheckerPayout.checker_id == checker.id,
            CheckerPayout.status == PayoutStatus.PENDING
        )
    ).count()
    
    return CheckerEarnings(
        total_usdc=checker.total_earnings,
        pending_payouts=pending_payouts,
        completed_chunks=checker.chunks_completed,
        average_rating=checker.average_rating
    )


@router.post("/register")
async def register_checker(
    wallet_address: str,
    whatsapp_number: str,
    full_name: str,
    country: str,
    telegram_username: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Register a new checker."""
    
    # Check if wallet already registered
    existing = db.query(Checker).filter(
        Checker.wallet_address == wallet_address
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=409, 
            detail="Wallet address already registered"
        )
    
    # Validate country code (simplified)
    if len(country) != 3:
        raise HTTPException(
            status_code=400, 
            detail="Country must be 3-letter ISO code"
        )
    
    # Create checker
    checker = Checker(
        wallet_address=wallet_address,
        whatsapp_number=whatsapp_number,
        full_name=full_name,
        country=country.upper(),
        telegram_username=telegram_username
    )
    
    db.add(checker)
    db.commit()
    
    return {"success": True, "checker_id": checker.id}


@router.get("/status/{chunk_id}")
async def get_chunk_status(
    chunk_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed status of a specific chunk."""
    
    chunk = db.query(DocChunk).filter(DocChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Get latest submission if any
    latest_submission = db.query(Submission).filter(
        Submission.chunk_id == chunk_id
    ).order_by(Submission.version.desc()).first()
    
    result = {
        "id": chunk.id,
        "status": chunk.status.value,
        "word_count": chunk.word_count,
        "claimed_by": chunk.claimed_by,
        "claimed_at": chunk.claimed_at,
        "completed_at": chunk.completed_at,
        "retry_count": chunk.retry_count,
        "turnitin_sim_score": chunk.turnitin_sim_score,
        "turnitin_ai_score": chunk.turnitin_ai_score,
        "flagged_spans": chunk.flagged_spans
    }
    
    if latest_submission:
        result["latest_submission"] = {
            "id": latest_submission.id,
            "version": latest_submission.version,
            "similarity_score": latest_submission.similarity_score,
            "ai_score": latest_submission.ai_score,
            "approved": latest_submission.approved,
            "submitted_at": latest_submission.submitted_at
        }
    
    return result