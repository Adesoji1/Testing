# app/services/language_services.py
# from app.schemas.language import LanguageCreate
# from app.models.language import Language
# from sqlalchemy.orm import Session
# from app.services.tts_service   import TTSService

# def get_all_languages(db: Session):
#     """Fetch all languages from the database."""
#     return db.query(Language).all()

# def add_language(db: Session, language_data: LanguageCreate):
#     """Add a new language to the database."""
#     existing_language = db.query(Language).filter(Language.code == language_data.code).first()
#     if existing_language:
#         raise ValueError("Language already exists")
#     new_language = Language(**language_data.dict())
#     db.add(new_language)
#     db.commit()
#     db.refresh(new_language)
#     return new_language

# def delete_language_by_id(db: Session, language_id: int):
#     """Delete a language by its ID."""
#     language = db.query(Language).filter(Language.id == language_id).first()
#     if not language:
#         raise ValueError("Language not found")
#     db.delete(language)
#     db.commit()
#     return True

# def detect_language_from_text(text: str, tts_service: TTSService):
#     """Simulate a detect language feature by using predefined mappings in TTSService."""
#     detected_language_code = "en"  # Simulated; replace with real language detection logic
#     voice_id, language_code = tts_service.get_voice_id_and_language_code(detected_language_code)
#     return {"language_code": language_code, "voice_id": voice_id}




# app/services/language_services.py
from app.schemas.language import LanguageCreate
from app.models.language import Language
from sqlalchemy.orm import Session
from app.services.tts_service   import TTSService

# Dummy language detection library; replace with a real one
from langdetect import detect  # Alternatively, integrate AWS Comprehend

def get_all_languages(db: Session, skip: int = 0, limit: int = 10):
    """Fetch all languages from the database."""
    return db.query(Language).offset(skip).limit(limit).all()


def add_language(db: Session, language_data: LanguageCreate):
    """Add a new language to the database."""
    existing_language = db.query(Language).filter(Language.code == language_data.code).first()
    if existing_language:
        raise ValueError("Language already exists")
    new_language = Language(**language_data.dict())
    db.add(new_language)
    db.commit()
    db.refresh(new_language)
    return new_language


def delete_language_by_id(db: Session, language_id: int):
    """Delete a language by its ID."""
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise ValueError("Language not found")
    db.delete(language)
    db.commit()
    return True


# def detect_language_from_text(text: str, tts_service: TTSService):
#     """Dynamically detect language using a library and map it to a voice ID."""
#     try:
#         # Use a library like `langdetect` to dynamically detect the language
#         detected_language_code = detect(text)  # E.g., 'en', 'es', 'de'
#         voice_id, language_code = tts_service.get_voice_id_and_language_code(detected_language_code)
#         return {"language_code": language_code, "voice_id": voice_id}
#     except Exception as e:
#         raise ValueError(f"Language detection failed: {str(e)}")

def detect_language_from_text(text: str, tts_service: TTSService):
    """Dynamically detect language using a library and map it to a voice ID."""
    try:
        # Detect language dynamically
        detected_language_code = detect(text)  # Example: 'en', 'es', 'de'
        voice_id, language_code = tts_service.get_voice_id_and_language_code(detected_language_code)
        return {"language_code": language_code, "voice_id": voice_id}
    except Exception as e:
        raise ValueError(f"Language detection failed: {str(e)}")
