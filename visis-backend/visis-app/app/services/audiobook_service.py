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



# def create_audiobook(
#     db: Session,
#     audiobook: AudioBookCreate,
#     file_path: Optional[str] = None,
# ) -> Audiobook:
#     """
#     Create a new audiobook record in the database and optionally process the audio file.

#     Args:
#         db (Session): Database session.
#         audiobook (AudioBookCreate): Audiobook schema.
#         file_path (Optional[str]): Path to the local audio file for processing.

#     Returns:
#         Audiobook: Created audiobook object.
#     """
#     try:
#         # Process the audio file locally if `file_path` is provided
#         if file_path:
#             processed_file_path = f"{file_path}_processed.mp3"
#             audio = AudioSegment.from_file(file_path, format="mp3")
#             audio.export(processed_file_path, format="mp3")
            
#             # Clean up the local file
#             os.remove(file_path)

#             # Upload processed file to S3
#             processed_audio_key = audiobook.file_key  # Use the `file_key` from the schema
#             processed_audio_url = s3_handler.upload_file(
#                 file_obj=open(processed_file_path, "rb"),
#                 bucket=settings.S3_BUCKET_NAME,
#                 key=processed_audio_key,
#                 content_type="audio/mpeg",
#             )

#             if not processed_audio_url:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Failed to upload processed audio to S3",
#                 )
            
#             # Update the audiobook URL with the processed audio URL
#             audiobook.url = processed_audio_url

#             # Remove the processed local file
#             os.remove(processed_file_path)

#         # Create the audiobook record in the database
#         db_audiobook = Audiobook(
#             title=audiobook.title,
#             author=audiobook.author,
#             narrator=audiobook.narrator,
#             duration=audiobook.duration,
#             genre=audiobook.genre,
#             publication_date=audiobook.publication_date,
#             file_key=audiobook.file_key,
#             url=audiobook.url,
#             is_dolby_atmos_supported=audiobook.is_dolby_atmos_supported,
#             document_id=audiobook.document_id,  # Set the document ID
#         )
#         db.add(db_audiobook)
#         db.commit()
#         db.refresh(db_audiobook)

#         return db_audiobook
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error creating audiobook: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to create audiobook record",
#         )

def create_audiobook(
    db: Session,
    audiobook: AudioBookCreate,
) -> Audiobook:
    """
    Create a new audiobook record in the database.

    Args:
        db (Session): Database session.
        audiobook (AudioBookCreate): Audiobook data.

    Returns:
        Audiobook: Created audiobook object.
    """
    try:
        # Create the audiobook record in the database
        db_audiobook = Audiobook(
            title=audiobook.title,
            author=audiobook.author,
            narrator=audiobook.narrator,
            duration=audiobook.duration,
            genre=audiobook.genre,
            publication_date=audiobook.publication_date,
            file_key=audiobook.file_key,
            url=audiobook.url,
            is_dolby_atmos_supported=audiobook.is_dolby_atmos_supported,
            document_id=audiobook.document_id,
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
            detail="Failed to create audiobook record",
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