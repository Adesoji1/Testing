# app/api/endpoints/user/preferences.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.schemas.enums import AudioFormat, ContentVisibility, FontSize, HighlightColor, PlaybackSpeed, ReadingMode, SupportedLanguages
from app.services.tts_service import TTSService


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
    text_to_speech_voice: str = Form(...),
    playback_speed: PlaybackSpeed = Form(...),
    audio_format: AudioFormat = Form(...),
    font_size: FontSize = Form(...),
    highlight_color: HighlightColor = Form(...),
    reading_mode: ReadingMode = Form(...),
    auto_save_bookmark: bool = Form(...),
    notification_enabled: bool = Form(...),
    default_folder: str = Form(...),
    content_visibility: ContentVisibility = Form(...),
    preferred_language: SupportedLanguages = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create preferences for the current user using form data."""
    existing_preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )
    if existing_preference:
        raise HTTPException(status_code=400, detail="Preferences already exist for this user")
    
    preference_data = {
        "text_to_speech_voice": text_to_speech_voice,
        "playback_speed": playback_speed,
        "audio_format": audio_format,
        "font_size": font_size,
        "highlight_color": highlight_color,
        "reading_mode": reading_mode,
        "auto_save_bookmark": auto_save_bookmark,
        "notification_enabled": notification_enabled,
        "default_folder": default_folder,
        "content_visibility": content_visibility,
        "preferred_language": preferred_language,
        "user_id": current_user.id
    }
    
    db_preference = UserPreference(**preference_data)
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

@router.put("/", response_model=UserPreferenceResponse)
def update_user_preferences(
    text_to_speech_voice: str = Form(None),
    playback_speed: PlaybackSpeed = Form(None),
    audio_format: AudioFormat = Form(None),
    font_size: FontSize = Form(None),
    highlight_color: HighlightColor = Form(None),
    reading_mode: ReadingMode = Form(None),
    auto_save_bookmark: bool = Form(None),
    notification_enabled: bool = Form(None),
    default_folder: str = Form(None),
    content_visibility: ContentVisibility = Form(None),
    preferred_language: SupportedLanguages = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the current user's preferences using form data."""
    db_preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )
    if not db_preference:
        # Optionally, create preferences if not found
        db_preference = UserPreference(user_id=current_user.id)
        db.add(db_preference)
    update_data = {
        k: v for k, v in {
            "text_to_speech_voice": text_to_speech_voice,
            "playback_speed": playback_speed,
            "audio_format": audio_format,
            "font_size": font_size,
            "highlight_color": highlight_color,
            "reading_mode": reading_mode,
            "auto_save_bookmark": auto_save_bookmark,
            "notification_enabled": notification_enabled,
            "default_folder": default_folder,
            "content_visibility": content_visibility,
            "preferred_language": preferred_language
        }.items() if v is not None
    }
    
    for field, value in update_data.items():
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

@router.get("/options")
def get_preference_options():
    """Get all available options for user preferences."""
    return {
        "playback_speeds": [speed.value for speed in PlaybackSpeed],
        "audio_formats": [format.value for format in AudioFormat],
        "font_sizes": [size.value for size in FontSize],
        "highlight_colors": [color.value for color in HighlightColor],
        "reading_modes": [mode.value for mode in ReadingMode],
        "content_visibility_options": [visibility.value for visibility in ContentVisibility],
        "supported_languages": [lang.value for lang in SupportedLanguages],
    }
