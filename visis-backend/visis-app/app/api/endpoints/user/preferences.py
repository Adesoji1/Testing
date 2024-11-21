

# app/api/endpoints/user/preferences.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.tts_service   import TTSService


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
        # Optionally, create default preferences if not found
        preference = UserPreference(user_id=current_user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
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
        # Optionally, create preferences if not found
        db_preference = UserPreference(user_id=current_user.id)
        db.add(db_preference)
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

@router.get("/voices", response_model=dict)
def get_voices_for_language(
    language_code: str,
    tts_service: TTSService = Depends()
):
    """Retrieve available voices for a given language."""
    language_voice_map = tts_service.get_all_language_voices()
    if language_code not in language_voice_map:
        raise HTTPException(status_code=400, detail="Unsupported language code")
    return {"language_code": language_code, "voices": language_voice_map[language_code]}
