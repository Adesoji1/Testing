# app/api/endpoints/user/languages.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from cachetools import TTLCache
from datetime import datetime

from app.models.language import Language
from app.schemas.language import (
    LanguageCreate,
    LanguageResponse,
    DetectLanguageResponse,
    LanguageStats,
    VoiceDetails
)
from app.database import get_db
from app.services.language_services import LanguageService
from app.services.tts_service import TTSService

router = APIRouter(prefix="/languages", tags=["Languages"])

# Initialize services
language_service = LanguageService()

@router.get("/", response_model=List[LanguageResponse])
async def list_languages(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    search: Optional[str] = None,
    sort_by: str = "name",
    db: Session = Depends(get_db)
):
    """List all supported languages with their voices."""
    try:
        languages = await language_service.get_languages(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            sort_by=sort_by
        )

        response = []
        for lang in languages:
            voices = await language_service.get_voices_for_language(lang.code)
            response.append(
                LanguageResponse(
                    id=lang.id,
                    name=lang.name,
                    code=lang.code,
                    display_name=lang.display_name if hasattr(lang, 'display_name') else None,
                    is_active=lang.is_active if hasattr(lang, 'is_active') else True,
                    native_name=lang.native_name if hasattr(lang, 'native_name') else None,
                    voices=voices,
                    created_at=lang.created_at if hasattr(lang, 'created_at') else datetime.utcnow(),
                    updated_at=lang.updated_at if hasattr(lang, 'updated_at') else None,
                    usage_count=lang.usage_count if hasattr(lang, 'usage_count') else 0
                )
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=LanguageStats)
async def get_language_statistics(db: Session = Depends(get_db)):
    """Get statistics about language usage."""
    return await language_service.get_language_stats(db)

@router.get("/{language_code}/voices", response_model=List[VoiceDetails])
async def get_language_voices(language_code: str):
    """Get available voices for a specific language."""
    voices = await language_service.get_voices_for_language(language_code)
    if not voices:
        # Return empty list instead of 404 error
        return []
    return voices

@router.post("/detect", response_model=DetectLanguageResponse)
async def detect_language(text: str):
    """Detect language from text and suggest voices."""
    try:
        return await language_service.detect_language(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=LanguageResponse)
async def create_language(
    language: LanguageCreate,
    db: Session = Depends(get_db)
):
    """Create a new language."""
    try:
        return await language_service.create_language(db, language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{language_id}", response_model=LanguageResponse)
async def update_language(
    language_id: int,
    language: LanguageCreate,
    db: Session = Depends(get_db)
):
    """Update an existing language."""
    try:
        return await language_service.update_language(db, language_id, language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{language_id}")
async def delete_language(
    language_id: int,
    db: Session = Depends(get_db)
):
    """Delete a language."""
    try:
        await language_service.delete_language(db, language_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/popular", response_model=List[LanguageResponse])
async def get_popular_languages(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get most popular languages based on usage."""
    try:
        languages = await language_service.get_popular_languages(db, limit)
        if not languages:
            return []
            
        response = []
        for lang in languages:
            voices = await language_service.get_voices_for_language(lang.code)
            response.append(
                LanguageResponse(
                    id=lang.id,
                    name=lang.name,
                    code=lang.code,
                    display_name=lang.display_name,
                    is_active=lang.is_active,
                    native_name=lang.native_name,
                    voices=voices,
                    created_at=lang.created_at,
                    updated_at=lang.updated_at,
                    usage_count=lang.usage_count or 0
                )
            )
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))