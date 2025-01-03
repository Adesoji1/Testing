# app/api/endpoints/user/views.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/views", tags=["Views"])

@router.post("/document/{document_id}/increment", status_code=status.HTTP_200_OK)
def increment_document_view(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Increment the 'play_count' for the specified Document by 1.
    This represents a user 'playing' or 'viewing' the audiobook.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.play_count += 1
    db.commit()
    db.refresh(doc)

    return {
        "message": "Play count incremented.",
        "document_id": doc.id,
        "play_count": doc.play_count
    }
