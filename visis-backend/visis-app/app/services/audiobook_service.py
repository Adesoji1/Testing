# services/audiobook_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from fastapi import HTTPException, status
from app.models import AudioBook
from app.schemas.audiobook import AudioBookCreate, AudioBookUpdate
from app.utils.s3_utils import s3_handler
from app.core.config import settings

logger = logging.getLogger(__name__)

def create_audiobook(
    db: Session,
    audiobook: AudioBookCreate,
    file_key: str
) -> AudioBook:
    """Create a new audiobook record."""
    try:
        db_audiobook = AudioBook(
            **audiobook.dict(),
            file_key=file_key,
            upload_date=datetime.utcnow()
        )
        db.add(db_audiobook)
        db.commit()
        db.refresh(db_audiobook)
        return db_audiobook
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating audiobook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create audiobook record"
        )

def get_audiobooks(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[AudioBook]:
    """Get a list of audiobooks."""
    try:
        return db.query(AudioBook).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error retrieving audiobooks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audiobooks"
        )

def update_audiobook(
    db: Session,
    audiobook_id: int,
    update_data: AudioBookUpdate
) -> AudioBook:
    """Update audiobook metadata."""
    try:
        audiobook = db.query(AudioBook).filter(AudioBook.id == audiobook_id).first()

        if not audiobook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audiobook not found"
            )

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(audiobook, field, value)

        db.commit()
        db.refresh(audiobook)
        return audiobook
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating audiobook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update audiobook"
        )

def delete_audiobook(db: Session, audiobook_id: int) -> bool:
    """Delete an audiobook."""
    try:
        audiobook = db.query(AudioBook).filter(AudioBook.id == audiobook_id).first()

        if not audiobook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audiobook not found"
            )

        # Delete file from S3
        if audiobook.file_key:
            s3_handler.delete_file(settings.S3_BUCKET_NAME, audiobook.file_key)

        # Delete database record
        db.delete(audiobook)
        db.commit()
        return True
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting audiobook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete audiobook"
        )