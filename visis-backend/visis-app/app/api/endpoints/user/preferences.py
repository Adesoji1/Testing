# preferences.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.user_preference import (
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
)
from app.core.security import get_current_user

router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=UserPreferenceResponse)
def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the current user's preferences."""
    preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )
    if not preference:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preference

@router.post("/", response_model=UserPreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_user_preferences(
    preference: UserPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create preferences for the current user."""
    existing_preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )
    if existing_preference:
        raise HTTPException(status_code=400, detail="Preferences already exist for this user")
    db_preference = UserPreference(**preference.dict(), user_id=current_user.id)
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

@router.put("/", response_model=UserPreferenceResponse)
def update_user_preferences(
    preference: UserPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the current user's preferences."""
    db_preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )
    if not db_preference:
        raise HTTPException(status_code=404, detail="Preferences not found")
    for field, value in preference.dict(exclude_unset=True).items():
        setattr(db_preference, field, value)
    db.commit()
    db.refresh(db_preference)
    return db_preference

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the current user's preferences."""
    preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )
    if not preference:
        raise HTTPException(status_code=404, detail="Preferences not found")
    db.delete(preference)
    db.commit()
    return None  # No content to return