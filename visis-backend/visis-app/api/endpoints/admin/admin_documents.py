from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import Document
from app.schemas.document import DocumentResponse
from app.database import SessionLocal
from app.core.security import get_current_user, oauth2_scheme
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.token import TokenData
from app.models.user import User
from app.core.security import get_current_admin_user

router = APIRouter(
    prefix="/admin/documents",
    tags=["admin-documents"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[DocumentResponse])
def list_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"detail": "Document deleted successfully"}