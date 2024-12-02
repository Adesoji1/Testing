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
from app.services.preference_services import iso_to_enum

from app.services.tts_service import TTSService  # Import the TTSService
from app.schemas.enums import SupportedLanguages  # Import SupportedLanguages Enum


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
    preference = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preference:
        # Optionally, create default preferences if not found
        preference = UserPreference(
            user_id=current_user.id,
            text_to_speech_voice="Joanna",
            playback_speed="1.0x",
            preferred_language="English"  # Default ISO code
        )
        db.add(preference)
        db.commit()
        db.refresh(preference)

    # Map the preferred_language from ISO to Enum (if needed)
    if preference.preferred_language:
        preference.preferred_language = iso_to_enum(preference.preferred_language)
    return preference

@router.post("/", response_model=UserPreferenceResponse, status_code=status.HTTP_201_CREATED,description="Create user preferences. [Available AWS Polly Voices](https://docs.aws.amazon.com/polly/latest/dg/available-voices.html)")
def create_user_preferences(
    preference: UserPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create preferences for the current user."""
    existing_preference = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if existing_preference:
        raise HTTPException(status_code=400, detail="Preferences already exist for this user.")
    # Convert Enum to ISO before saving
    preference_data = preference.dict()
    preference_data["preferred_language"] = preference.preferred_language.value.lower()[:2]  # 'English' -> 'en'
    db_preference = UserPreference(**preference_data, user_id=current_user.id)
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
    db_preference = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not db_preference:
        # Optionally, create preferences if not found
        db_preference = UserPreference(user_id=current_user.id)
        db.add(db_preference)
    for field, value in preference.dict(exclude_unset=True).items():
        if field == "preferred_language" and value:
            # Convert Enum to ISO before updating
            value = value.value.lower()[:2]  # 'English' -> 'en'
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
    return None



@router.get("/voices", response_model=dict)
def get_voices_for_language(
    language: SupportedLanguages,
    tts_service: TTSService = Depends()
):
    """
    Get available voices for the selected language.
    
    Args:
        language (SupportedLanguages): The preferred language.
        tts_service (TTSService): Injected TTSService dependency.

    Returns:
        dict: Language and available voices.
    """
    # Get the language-to-voice mappings
    voice_map = tts_service.get_all_language_voices()
    
    # Fetch the voices for the given language
    voices = voice_map.get(language.value.lower(), [])
    
    # If no voices are available, return an error
    if not voices:
        raise HTTPException(
            status_code=400,
            detail=f"No voices available for the selected language: {language.value}."
        )
    
    # Return the language and its voices
    return {"language": language.value, "voices": voices}
