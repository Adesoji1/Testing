# app/services/language_services.py

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from app.models.language import Language
from app.schemas.language import (
    LanguageCreate,
    LanguageUpdate,
    LanguageStats,
    VoiceDetails,
    DetectLanguageResponse,
    PopularLanguage
)
from app.core.cache import cache_response, invalidate_cache

class LanguageService:
    def __init__(self, region_name: str = 'us-east-1'):
        self.comprehend = boto3.client('comprehend', region_name=region_name)
        self.polly = boto3.client('polly', region_name=region_name)

    @cache_response(ttl=3600, prefix="languages")
    async def get_languages(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "name"
    ) -> List[Language]:
        query = db.query(Language)
        
        if search:
            query = query.filter(
                Language.name.ilike(f"%{search}%") |
                Language.code.ilike(f"%{search}%")
            )
            
        order_col = getattr(Language, sort_by)
        return query.order_by(order_col).offset(skip).limit(limit).all()

    async def create_language(
        self,
        db: Session,
        language: LanguageCreate
    ) -> Language:
        db_language = Language(**language.dict())
        db.add(db_language)
        try:
            db.commit()
            db.refresh(db_language)
            invalidate_cache("languages")
            return db_language
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_voices_for_language(
        self,
        language_code: str
    ) -> List[VoiceDetails]:
        try:
            response = self.polly.describe_voices(LanguageCode=language_code)
            return [
                VoiceDetails(
                    id=voice['Id'],
                    name=voice['Name'],
                    gender=voice['Gender'],
                    language_code=voice['LanguageCode'],
                    engine=voice.get('SupportedEngines', ['standard'])[0],
                    supported_features=voice.get('SupportedEngines', [])
                )
                for voice in response['Voices']
            ]
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @cache_response(ttl=3600, prefix="language_stats")
    async def get_language_stats(self, db: Session) -> LanguageStats:
        try:
            # Get counts
            total = db.query(func.count(Language.id)).scalar()
            active = db.query(func.count(Language.id)).filter(Language.is_active == True).scalar()
            
            # Get usage stats
            usage_query = (
                db.query(Language.code, func.count(Language.id))
                .group_by(Language.code)
                .all()
            )
            
            # Get popular languages
            popular = (
                db.query(Language)
                .filter(Language.is_active == True)
                .order_by(Language.usage_count.desc())
                .limit(5)
                .all()
            )

            return LanguageStats(
                total_languages=total,
                active_languages=active,
                total_voices=len(self.get_supported_voices()),
                language_usage={code: count for code, count in usage_query},
                popular_languages=[
                    PopularLanguage(
                        code=lang.code,
                        name=lang.name,
                        usage_count=lang.usage_count or 0,
                        last_used=lang.updated_at or lang.created_at
                    )
                    for lang in popular
                ],
                last_updated=datetime.utcnow()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting language stats: {str(e)}")

    async def get_voices_for_language(self, language_code: str) -> List[VoiceDetails]:
        """Get available voices for a specific language code."""
        try:
            aws_code = self.get_aws_language_code(language_code)
            response = self.polly.describe_voices(LanguageCode=aws_code)
            return [
                VoiceDetails(
                    id=voice['Id'],
                    name=voice['Name'],
                    gender=voice['Gender'].lower(),
                    language_code=voice['LanguageCode'],
                    engine=voice.get('SupportedEngines', ['standard'])[0],
                    supported_features=voice.get('SupportedEngines', [])
                )
                for voice in response['Voices']
            ]
        except ClientError as e:
            # Return empty list instead of raising exception for better handling
            return []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting voices: {str(e)}")

    def get_aws_language_code(self, code: str) -> str:
        """Map language codes to AWS format."""
        code_map = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'pt': 'pt-BR',
            'zh': 'zh-CN',
        }
        # If code already contains region (e.g., en-GB), return as is
        if '-' in code:
            return code
        return code_map.get(code, f"{code}-{code.upper()}")

    def get_supported_voices(self) -> List[Dict]:
        """Get all supported voices."""
        try:
            response = self.polly.describe_voices()
            return response['Voices']
        except ClientError:
            return []


    async def detect_language(self, text: str) -> DetectLanguageResponse:
        try:
            response = self.comprehend.detect_dominant_language(Text=text)
            languages = response['Languages']
            
            if not languages:
                raise HTTPException(
                    status_code=400,
                    detail="Could not detect language"
                )
                
            primary = languages[0]
            voices = await self.get_voices_for_language(primary['LanguageCode'])
            
            return DetectLanguageResponse(
                detected_language=primary['LanguageCode'],
                confidence=primary['Score'],
                alternative_languages=[
                    {l['LanguageCode']: l['Score']}
                    for l in languages[1:]
                ],
                suggested_voices=voices
            )
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def validate_voice_language_pair(
        self,
        voice_id: str,
        language_code: str
    ) -> bool:
        voices = await self.get_voices_for_language(language_code)
        return any(v.id == voice_id for v in voices)

    async def _get_total_voices_count(self) -> int:
        try:
            response = self.polly.describe_voices()
            return len(response['Voices'])
        except ClientError:
            return 0

    async def update_language(
        self,
        db: Session,
        language_id: int,
        language: LanguageUpdate
    ) -> Language:
        db_language = db.query(Language).filter(Language.id == language_id).first()
        if not db_language:
            raise HTTPException(status_code=404, detail="Language not found")
            
        for key, value in language.dict(exclude_unset=True).items():
            setattr(db_language, key, value)
            
        try:
            db.commit()
            db.refresh(db_language)
            invalidate_cache("languages")
            return db_language
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_popular_languages(
        self,
        db: Session,
        limit: int = 5
    ) -> List[Language]:
        """Get most popular languages based on usage count."""
        try:
            return (
                db.query(Language)
                .filter(Language.is_active == True)
                .order_by(Language.usage_count.desc())
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching popular languages: {str(e)}"
            )