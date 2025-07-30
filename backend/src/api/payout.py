from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Assuming your models and db setup are in these locations
from db.database import get_db
from db.models import CheckerPayout, Checker

router = APIRouter(
    prefix="/payouts",
    tags=["payouts"],
    responses={404: {"description": "Not found"}},
)

# A placeholder for getting the current checker's ID, e.g., from a JWT
def get_current_checker_id() -> int:
    # In a real app, you'd decode a JWT token here.
    # For now, we'll return a hardcoded ID for testing.
    return 1

@router.get("/earnings")
def get_checker_earnings(db: Session = Depends(get_db), checker_id: int = Depends(get_current_checker_id)):
    """
    Get the earnings for the current checker.
    Returns a list of all their payouts and a summary.
    """
    payouts = db.query(CheckerPayout).filter(CheckerPayout.checker_id == checker_id).all()

    total_earned = sum(p.amount_pence for p in payouts if p.status == 'paid')
    pending_payout = sum(p.amount_pence for p in payouts if p.status == 'pending')

    return {
        "payouts": payouts,
        "summary": {
            "total_earned_pence": total_earned,
            "pending_payout_pence": pending_payout,
        }
    }

# This endpoint is more for internal use by the application logic
# when a chunk is approved, not directly by the user.
@router.post("/credit", status_code=201)
def credit_payout_for_approval(checker_id: int, chunk_id: int, amount_pence: int, db: Session = Depends(get_db)):
    """
    Creates a new 'pending' payout record when a chunk is approved.
    This is typically called by another service or agent after the rewrite
    and re-check loop is successfully completed.
    """
    checker = db.query(Checker).filter(Checker.id == checker_id).first()
    if not checker:
        raise HTTPException(status_code=404, detail=f"Checker with id {checker_id} not found.")

    new_payout = CheckerPayout(
        checker_id=checker_id,
        chunk_id=chunk_id,
        amount_pence=amount_pence,
        status='pending' # Initial status
    )
    db.add(new_payout)
    db.commit()
    db.refresh(new_payout)

    return {"message": "Payout credited successfully.", "payout": new_payout}