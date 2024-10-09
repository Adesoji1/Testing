from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import UserPreference, User
from app.schemas.user_preference import UserPreferenceCreate, UserPreferenceResponse
from app.database import SessionLocal
from app.core.security import get_current_user

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UserPreferenceResponse])
def list_preferences(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).offset(skip).limit(limit).all()
    return preferences

@router.post("/", response_model=UserPreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_preference(preference: UserPreferenceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_preference = UserPreference(**preference.dict(), user_id=current_user.id)
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

@router.delete("/{preference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(preference_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    preference = db.query(UserPreference).filter(UserPreference.id == preference_id, UserPreference.user_id == current_user.id).first()
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(preference)
    db.commit()
    return {"detail": "Preference deleted successfully"}