from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import StudyCircle, StudyCircleMember, StudyCircleDocument, User, Document
from src.services.supabase_service import get_supabase_client

router = APIRouter(
    prefix="/api/circle",
    tags=["study-circle"],
)

# A placeholder for getting the current user's ID
def get_current_user_id() -> str:
    # In a real app, this would come from a JWT token
    return "some-hardcoded-user-id" # Replace with a valid UUID from your db for testing

@router.post("/create")
def create_study_circle(name: str, db: Session = Depends(get_db), owner_id: str = Depends(get_current_user_id)):
    """Creates a new study circle."""
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    new_circle = StudyCircle(name=name, owner_id=owner.id)
    db.add(new_circle)
    db.commit()
    db.refresh(new_circle)
    return {"message": "Study circle created successfully", "circle_id": str(new_circle.id)}

@router.post("/{circle_id}/join")
def join_study_circle(circle_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Adds the current user to a study circle."""
    circle = db.query(StudyCircle).filter(StudyCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Study circle not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    membership = StudyCircleMember(circle_id=circle.id, user_id=user.id)
    db.add(membership)
    db.commit()
    return {"message": f"Successfully joined circle '{circle.name}'"}

@router.post("/{circle_id}/share")
def share_document_to_circle(circle_id: str, document_id: str, db: Session = Depends(get_db)):
    """Shares a document with a study circle."""
    circle = db.query(StudyCircle).filter(StudyCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Study circle not found")

    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    sharing = StudyCircleDocument(circle_id=circle.id, document_id=doc.id)
    db.add(sharing)
    db.commit()
    return {"message": "Document shared successfully"}

@router.post("/{circle_id}/message")
async def send_circle_message(circle_id: str, message: str, user_id: str = Depends(get_current_user_id)):
    """Sends a real-time message to a study circle via Supabase."""
    supabase = get_supabase_client()
    channel = supabase.channel(f"study_circle_{circle_id}")
    
    payload = {
        "event": "new_message",
        "payload": {
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    await channel.send(payload)
    return {"message": "Message sent"}