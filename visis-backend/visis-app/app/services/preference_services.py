from sqlalchemy.orm import Session
from app.models.user_preference import UserPreference
from app.models.user import User
from app.schemas.enums import SupportedLanguages

def get_or_create_default_preferences(db: Session, user: User) -> UserPreference:
    """Retrieve user preferences or create default ones."""
    preferences = db.query(UserPreference).filter(UserPreference.user_id == user.id).first()
    if not preferences:
        preferences = UserPreference(
            user_id=user.id,
            text_to_speech_voice="default",
            playback_speed="1x",
            preferred_language="English",
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    return preferences


# Utility function to map ISO codes to SupportedLanguages
def iso_to_enum(iso_code: str) -> SupportedLanguages:
    iso_to_language_map = {
        'en': SupportedLanguages.English,
        'es': SupportedLanguages.Spanish,
        'de': SupportedLanguages.German,
        'it': SupportedLanguages.Italian,
        'fr': SupportedLanguages.French,
        'pt': SupportedLanguages.Portuguese,
    }
    return iso_to_language_map.get(iso_code, SupportedLanguages.English)  # Default to English
