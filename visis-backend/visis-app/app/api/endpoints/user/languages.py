from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import Language, User
from app.schemas.language import LanguageCreate, LanguageResponse
from app.database import SessionLocal
from app.core.security import get_current_user

router = APIRouter(
    prefix="/languages",
    tags=["languages"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[LanguageResponse])
def list_languages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    languages = db.query(Language).offset(skip).limit(limit).all()
    return languages

@router.post("/", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
def create_language(language: LanguageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_language = Language(**language.dict())
    db.add(db_language)
    db.commit()
    db.refresh(db_language)
    return db_language

@router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_language(language_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    db.delete(language)
    db.commit()
    return {"detail": "Language deleted successfully"}