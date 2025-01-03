# services/audiobook_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import os

from fastapi import HTTPException, status
from app.models import Audiobook
from app.schemas.audiobook import AudioBookCreate, AudioBookUpdate
from app.utils.s3_utils import s3_handler
from app.core.config import settings
from pydub import AudioSegment

logger = logging.getLogger(__name__)


def create_audiobook(db: Session, audiobook_data: AudioBookCreate) -> Audiobook:
    """Create a new Audiobook record in the database."""
    try:
        audiobook = Audiobook(
            title=audiobook_data.title,
            author=audiobook_data.author,
            narrator=audiobook_data.narrator,
            duration=audiobook_data.duration,
            genre=audiobook_data.genre,
            publication_date=audiobook_data.publication_date,
            file_key=audiobook_data.file_key,
            is_dolby_atmos_supported=audiobook_data.is_dolby_atmos_supported,
            url=audiobook_data.url,
            document_id=audiobook_data.document_id
        )
        db.add(audiobook)
        db.commit()
        db.refresh(audiobook)
        logger.info(f"Audiobook created with ID {audiobook.id} for Document ID {audiobook.document_id}.")
        return audiobook
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating audiobook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audiobook: {str(e)}"
        )


def get_audiobooks(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[Audiobook]:
    """Get a list of audiobooks."""
    try:
        return db.query(Audiobook).offset(skip).limit(limit).all()
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
) -> Audiobook:
    """Update audiobook metadata."""
    try:
        audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()

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
        audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()

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