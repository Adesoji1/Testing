# # app/api/endpoints/user/languages.py


# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from app.models.language import Language
# from app.schemas.language import LanguageCreate, LanguageResponse, DetectLanguageResponse
# from app.services.language_services import (
#     get_all_languages,
#     add_language,
#     delete_language_by_id,
#     detect_language_from_text,
# )
# from app.database import get_db
# from app.services.tts_service import TTSService

# router = APIRouter(
#     prefix="/languages",
#     tags=["Languages"],
#     responses={404: {"description": "Not found"}},
# )



# @router.get("/", response_model=List[LanguageResponse])
# def list_languages(
#     db: Session = Depends(get_db),
#     tts_service: TTSService = Depends()
# ):
#     """
#     Retrieve all languages with their supported voices.
#     """
#     # Query all languages from the database
#     languages = db.query(Language).all()

#     # Fetch the voice mappings from TTSService
#     voice_map = tts_service.get_all_language_voices()

#     # Populate the voices field dynamically for each language
#     result = []
#     for language in languages:
#         result.append({
#             "id": language.id,
#             "name": language.name,
#             "code": language.code,
#             "voices": voice_map.get(language.code, [])
#         })

#     return result

#     # # Build the response with voices
#     # response = [
#     #     LanguageResponse(
#     #         id=language.id,
#     #         name=language.name,
#     #         code=language.code,
#     #         voices=voice_map.get(language.code, [])  # Get voices for the language code
#     #     )
#     #     for language in languages
#     # ]
#     # return response


# @router.post("/", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
# def create_language(
#     language: LanguageCreate,
#     db: Session = Depends(get_db)
# ):
#     """Add a new language to the database."""
#     try:
#         return add_language(db, language)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_language(
#     language_id: int,
#     db: Session = Depends(get_db)
# ):
#     """Delete a language by its ID."""
#     try:
#         return delete_language_by_id(db, language_id)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))





# @router.post("/detect", response_model=DetectLanguageResponse)
# def detect_language(
#     text: str,
#     tts_service: TTSService = Depends()
# ):
#     """Detect language from text and return voice options."""
#     return detect_language_from_text(text, tts_service)


# # Define the PUT endpoint
# @router.put("/{language_id}", response_model=LanguageResponse, status_code=status.HTTP_200_OK)
# def update_language(
#     language_id: int,
#     language_update: LanguageCreate,
#     db: Session = Depends(get_db),
# ):
#     """
#     Update an existing language.
#     """
#     # Retrieve the language by its ID
#     language = db.query(Language).filter(Language.id == language_id).first()
#     if not language:
#         raise HTTPException(status_code=404, detail="Language not found")
    
#     # Update the language attributes
#     language.name = language_update.name
#     language.code = language_update.code
    
#     # Commit the changes
#     db.commit()
#     db.refresh(language)
    
#     return language


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.language import Language
from app.schemas.language import LanguageCreate, LanguageResponse, DetectLanguageResponse
from app.services.language_services import (
    get_all_languages,
    add_language,
    delete_language_by_id,
    detect_language_from_text,
)
from app.database import get_db
from app.services.tts_service import TTSService

router = APIRouter(
    prefix="/languages",
    tags=["Languages"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[LanguageResponse])
def list_languages(
    db: Session = Depends(get_db),
    tts_service: TTSService = Depends()
):
    """
    Retrieve all languages with their supported voices dynamically.
    """
    # Query all languages from the database
    languages = db.query(Language).all()

    # Fetch the voice mappings from TTSService
    voice_map = tts_service.get_all_language_voices()

    # Build the response with voices
    response = [
        LanguageResponse(
            id=language.id,
            name=language.name,
            code=language.code,
            voices=voice_map.get(language.code, [])  # Get voices for the language code
        )
        for language in languages
    ]
    return response


@router.post("/", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
def create_language(
    language: LanguageCreate,
    db: Session = Depends(get_db)
):
    """Add a new language to the database."""
    try:
        return add_language(db, language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_language(
    language_id: int,
    db: Session = Depends(get_db)
):
    """Delete a language by its ID."""
    try:
        return delete_language_by_id(db, language_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/detect", response_model=DetectLanguageResponse)
def detect_language(
    text: str,
    tts_service: TTSService = Depends()
):
    """Detect language from text and return voice options."""
    return detect_language_from_text(text, tts_service)


@router.put("/{language_id}", response_model=LanguageResponse, status_code=status.HTTP_200_OK)
def update_language(
    language_id: int,
    language_update: LanguageCreate,
    db: Session = Depends(get_db),
):
    """
    Update an existing language.
    """
    # Retrieve the language by its ID
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    # Update the language attributes
    language.name = language_update.name
    language.code = language_update.code
    
    # Commit the changes
    db.commit()
    db.refresh(language)
    
    return language
