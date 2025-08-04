from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import datetime
import os

# Standardized imports to src.* package root
from src.db.database import get_db
from src.db.models import DocChunk, Submission

# Environment variables for configuration
MAX_CLAIMS_PER_CHECKER = int(os.getenv("MAX_CLAIMS_PER_CHECKER", 3))
TIMEOUT_CHECK_MIN = int(os.getenv("TIMEOUT_CHECK_MIN", 15))

router = APIRouter(
    prefix="/checker",
    tags=["checker"],
    responses={404: {"description": "Not found"}},
)

# A placeholder for getting the current checker's ID, e.g., from a JWT
def get_current_checker_id() -> int:
    # In a real app, you'd decode a JWT token here.
    # For now, we'll return a hardcoded ID for testing.
    return 1

@router.get("/chunks")
def get_available_chunks(status: str = "open", db: Session = Depends(get_db)):
    """
    Get a list of document chunks available for checking.
    Filters by status (e.g., 'open', 'needs_edit').
    """
    chunks = db.query(DocChunk).filter(DocChunk.status == status).all()
    return chunks

@router.post("/claim/{chunk_id}")
def claim_chunk(chunk_id: int, db: Session = Depends(get_db), checker_id: int = Depends(get_current_checker_id)):
    """
    Allows a checker to claim a chunk for processing.
    """
    # Check if the checker has too many active claims
    active_claims = db.query(DocChunk).filter(
        DocChunk.checker_id == checker_id,
        DocChunk.status == 'checking'
    ).count()

    if active_claims >= MAX_CLAIMS_PER_CHECKER:
        raise HTTPException(
            status_code=400,
            detail=f"You cannot have more than {MAX_CLAIMS_PER_CHECKER} active claims."
        )

    # Find the chunk and claim it
    chunk = db.query(DocChunk).filter(DocChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found.")
    if chunk.status != 'open':
        raise HTTPException(status_code=400, detail="This chunk is not available for claiming.")

    chunk.status = 'checking'
    chunk.checker_id = checker_id
    chunk.claim_timestamp = datetime.datetime.utcnow()
    db.commit()
    db.refresh(chunk)

    return {"message": "Chunk claimed successfully.", "chunk": chunk}


@router.post("/submit/{chunk_id}")
async def submit_chunk_review(
    chunk_id: int,
    sim_pdf: UploadFile = File(...),
    ai_pdf: UploadFile = File(...),
    flagged: List[str] = Form(...),
    db: Session = Depends(get_db),
    checker_id: int = Depends(get_current_checker_id)
):
    """
    Submit the results of a chunk review.
    This includes the two PDF reports and a list of flagged text snippets.
    """
    chunk = db.query(DocChunk).filter(DocChunk.id == chunk_id, DocChunk.checker_id == checker_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found or not assigned to you.")
    if chunk.status != 'checking':
        raise HTTPException(status_code=400, detail="This chunk is not in a 'checking' state.")

    # --- File Upload Logic (Stubbed) ---
    # In a real app, you would stream these files to S3 or another object store.
    # For this example, we'll just confirm we received them.
    sim_pdf_filename = f"submissions/{chunk_id}_{checker_id}_sim.pdf"
    ai_pdf_filename = f"submissions/{chunk_id}_{checker_id}_ai.pdf"
    # await save_upload_file(sim_pdf, sim_pdf_filename)
    # await save_upload_file(ai_pdf, ai_pdf_filename)
    print(f"Received files: {sim_pdf.filename}, {ai_pdf.filename}")
    print(f"Would be saved to: {sim_pdf_filename}, {ai_pdf_filename}")
    # --- End File Upload Logic ---

    # Create a new submission record
    submission = Submission(
        chunk_id=chunk_id,
        checker_id=checker_id,
        similarity_report_url=sim_pdf_filename, # URL from storage
        ai_report_url=ai_pdf_filename, # URL from storage
        flagged_json={"flags": flagged},
        version=chunk.current_version + 1 # Increment version
    )
    db.add(submission)

    # Update the chunk's status based on the submission
    # This is a simplified logic. A real system might have more complex rules.
    if not flagged:
        chunk.status = 'done' # No issues found, chunk is done
    else:
        chunk.status = 'needs_edit' # Issues found, needs rewrite

    chunk.current_version += 1
    db.commit()
    db.refresh(chunk)
    db.refresh(submission)

    return {"message": "Submission successful.", "chunk_status": chunk.status, "submission_id": submission.id}
