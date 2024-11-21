# # document_service.py

# import io
# import logging
# import asyncio
# from datetime import datetime
# from typing import List, Optional
# from pydub.effects import normalize

# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status

# from app.database import SessionLocal
# from app.models import Document
# from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentFilter
# from app.utils.s3_utils import s3_handler
# from app.services.ocr_service import OCRService
# from app.services.tts_service import TTSService
# from app.core.config import settings

# logger = logging.getLogger(__name__)

# # Initialize services
# ocr_service = OCRService(region_name='us-east-1')
# tts_service = TTSService(region_name='us-east-1')

# def create_document(
#     db: Session,
#     document: DocumentCreate,
#     user_id: int,
#     file_key: str,
#     file_size: Optional[int] = None
# ) -> Document:
#     """Create a new document record."""
#     try:
#         db_document = Document(
#             **document.dict(exclude={"file_key"}),  # Exclude file_key from the dict
#             user_id=user_id,
#             file_key=file_key,  # Pass file_key explicitly
#             file_size=file_size,
#             upload_date=datetime.utcnow()
#         )
#         db.add(db_document)
#         db.commit()
#         db.refresh(db_document)
#         return db_document
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error creating document: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to create document record"
#         )

# def get_documents(
#     db: Session,
#     user_id: int,
#     filter_params: DocumentFilter,
#     skip: int = 0,
#     limit: int = 10
# ) -> List[Document]:
#     """Get documents with filtering."""
#     try:
#         query = db.query(Document).filter(Document.user_id == user_id)

#         if filter_params.search:
#             query = query.filter(Document.title.ilike(f"%{filter_params.search}%"))

#         if filter_params.status:
#             query = query.filter(Document.processing_status == filter_params.status)

#         if filter_params.file_type:
#             query = query.filter(Document.file_type == filter_params.file_type)

#         if filter_params.start_date:
#             query = query.filter(Document.upload_date >= filter_params.start_date)

#         if filter_params.end_date:
#             query = query.filter(Document.upload_date <= filter_params.end_date)

#         return query.offset(skip).limit(limit).all()
#     except Exception as e:
#         logger.error(f"Error retrieving documents: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve documents"
#         )

# def update_document(
#     db: Session,
#     document_id: int,
#     user_id: int,
#     update_data: DocumentUpdate
# ) -> Document:
#     """Update document metadata."""
#     try:
#         document = db.query(Document).filter(
#             Document.id == document_id,
#             Document.user_id == user_id
#         ).first()

#         if not document:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Document not found"
#             )

#         for field, value in update_data.dict(exclude_unset=True).items():
#             setattr(document, field, value)

#         db.commit()
#         db.refresh(document)
#         return document
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error updating document: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update document"
#         )

# def delete_document(db: Session, document_id: int, user_id: int) -> bool:
#     """Delete document and associated files."""
#     try:
#         document = db.query(Document).filter(
#             Document.id == document_id,
#             Document.user_id == user_id
#         ).first()

#         if not document:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Document not found"
#             )

#         # Delete files from S3
#         if document.file_key:
#             s3_handler.delete_file(settings.S3_BUCKET_NAME, document.file_key)
#         if document.audio_key:
#             s3_handler.delete_file(settings.S3_BUCKET_NAME, document.audio_key)

#         # Delete database record
#         db.delete(document)
#         db.commit()
#         return True
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error deleting document: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to delete document"
#         )

# async def process_document(document_id: int):
#     """Process document for OCR and TTS."""
#     db = SessionLocal()
#     try:
#         document = db.query(Document).filter(Document.id == document_id).first()
#         if not document:
#             logger.error(f"Document {document_id} not found")
#             return

#         document.processing_status = 'processing'
#         db.commit()

#         # Extract text based on file type
#         if document.file_type == 'application/pdf':
#             text, _ = await ocr_service.extract_text_from_pdf(settings.S3_BUCKET_NAME, document.file_key)
#         elif document.file_type.startswith('image/'):
#             text, _ = await ocr_service.extract_text_from_image(settings.S3_BUCKET_NAME, document.file_key)
#         else:
#             # For text files stored locally or other types
#             s3_object = await asyncio.get_event_loop().run_in_executor(
#                 None,
#                 lambda: s3_handler.s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=document.file_key)
#             )
#             text = s3_object['Body'].read().decode('utf-8')

#         # Split text into chunks of <= 3000 characters
#         max_length = 3000
#         text_chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]

#         # Generate audio for each chunk and concatenate
#         audio_bytes_io = io.BytesIO()
#         for chunk in text_chunks:
#             chunk_audio = await tts_service.convert_text_to_speech(chunk)
#             audio_bytes_io.write(chunk_audio)

#         audio_bytes_io.seek(0)  # Reset the cursor to the beginning

#         # Upload audio file
#         audio_key = f"{settings.S3_FOLDER_NAME}/audio/{document.user_id}/{document.id}.mp3"
#         audio_url = await s3_handler.upload_file(
#             audio_bytes_io,
#             settings.S3_BUCKET_NAME,
#             audio_key,
#             'audio/mpeg'
#         )
#         # Log the generated audio URL
#         logger.info(f"Generated audio URL: {audio_url}")

#         # Update document
#         document.audio_url = audio_url
#         document.audio_key = audio_key
#         document.processing_status = 'completed'
#         db.commit()
#         # Log document update
#         logger.info(f"Document {document_id} updated with audio URL: {audio_url}")
#     except Exception as e:
#         logger.error(f"Error processing document {document_id}: {str(e)}")
#         if document:
#             document.processing_status = 'failed'
#             document.processing_error = str(e)
#             db.commit()
#     finally:
#         db.close()




# def apply_immersive_effects(audio):
#     """Apply immersive audio effects."""
#     audio = normalize(audio)
#     left = audio.pan(-0.5)
#     right = audio.pan(0.5)
#     return left.overlay(right)



import io
import logging
from datetime import datetime
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from pydub.effects import normalize
from pydub import AudioSegment

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database import SessionLocal
from app.models import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentFilter
from app.utils.s3_utils import s3_handler
from app.services.ocr_service import OCRService
from app.services.tts_service import TTSService
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize services
ocr_service = OCRService(region_name='us-east-1')
tts_service = TTSService(region_name='us-east-1')


def apply_immersive_effects(audio: AudioSegment) -> AudioSegment:
    """Apply immersive audio effects."""
    audio = normalize(audio)  # Normalize audio volume
    left = audio.pan(-0.5)  # Pan slightly to the left
    right = audio.pan(0.5)  # Pan slightly to the right
    return left.overlay(right)

def update_document(
    db: Session,
    document_id: int,
    user_id: int,
    document_update: DocumentUpdate
) -> Document:
    """Update an existing document record."""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Update the document fields
        for key, value in document_update.dict(exclude_unset=True).items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)
        return document
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document"
        )



def create_document(
    db: Session,
    document: DocumentCreate,
    user_id: int,
    file_key: str,
    file_size: Optional[int] = None
) -> Document:
    """Create a new document record."""
    try:
        db_document = Document(
            **document.dict(exclude={"file_key"}),  # Exclude file_key from the dict
            user_id=user_id,
            file_key=file_key,  # Pass file_key explicitly
            file_size=file_size,
            upload_date=datetime.utcnow()
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create document record"
        )

def get_documents(
    db: Session,
    user_id: int,
    filter_params: DocumentFilter,
    skip: int = 0,
    limit: int = 10
) -> List[Document]:
    """Get documents with filtering."""
    try:
        query = db.query(Document).filter(Document.user_id == user_id)

        if filter_params.search:
            query = query.filter(Document.title.ilike(f"%{filter_params.search}%"))

        if filter_params.status:
            query = query.filter(Document.processing_status == filter_params.status)

        if filter_params.file_type:
            query = query.filter(Document.file_type == filter_params.file_type)

        if filter_params.start_date:
            query = query.filter(Document.upload_date >= filter_params.start_date)

        if filter_params.end_date:
            query = query.filter(Document.upload_date <= filter_params.end_date)

        return query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


def process_text_chunks_in_parallel(text_chunks, detected_language):
    """Process text chunks for TTS in parallel."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(
            lambda chunk: tts_service.convert_text_to_speech(chunk, detected_language),
            text_chunks
        ))


def generate_audio_for_document(document: Document, text: str, detected_language: str):
    """Generate audio for a document and upload to S3."""
    try:
        # Split text into manageable chunks
        max_length = 3000
        text_chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]

        # Process chunks in parallel
        audio_chunks = process_text_chunks_in_parallel(text_chunks, detected_language)

        # Combine audio chunks into one audio file
        audio_bytes_io = io.BytesIO()
        for chunk_audio in audio_chunks:
            audio_bytes_io.write(chunk_audio)

        # Apply immersive audio effects
        audio_bytes_io.seek(0)
        audio = AudioSegment.from_file(audio_bytes_io, format="mp3")
        immersive_audio = apply_immersive_effects(audio)

        # Export processed audio to a BytesIO object
        processed_audio_io = io.BytesIO()
        immersive_audio.export(processed_audio_io, format="mp3", bitrate="64k")
        processed_audio_io.seek(0)

        # Upload processed audio to S3
        processed_audio_key = f"{settings.S3_FOLDER_NAME}/audio/{document.user_id}/{document.id}_processed.mp3"
        audio_url = s3_handler.upload_file(
            file_obj=processed_audio_io,
            bucket=settings.S3_BUCKET_NAME,
            key=processed_audio_key,
            content_type="audio/mpeg",
        )
        if not audio_url:
            raise Exception("Failed to upload audio to S3")

        return audio_url, processed_audio_key
    except Exception as e:
        logger.error(f"Error generating audio for document {document.id}: {str(e)}")
        raise e


def process_document(document_id: int):
    """Process document for OCR and TTS."""
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return

        document.processing_status = 'processing'
        db.commit()

        # Extract text based on file type
        if document.file_type == 'application/pdf':
            text, detected_language = ocr_service.extract_text_from_pdf(
                bucket_name=settings.S3_BUCKET_NAME,
                file_key=document.file_key
            )
        elif document.file_type.startswith('image/'):
            text, detected_language = ocr_service.extract_text_from_image(
                bucket_name=settings.S3_BUCKET_NAME,
                file_key=document.file_key
            )
        elif document.file_type == "text/plain":
            s3_object = s3_handler.s3_client.get_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=document.file_key
            )
            text = s3_object['Body'].read().decode('utf-8')
            detected_language = 'en'
        else:
            raise Exception("Unsupported file type")

        if not text.strip():
            raise Exception("No text found in the document")

        # Generate audio and upload to S3
        audio_url, processed_audio_key = generate_audio_for_document(document, text, detected_language)

        # Update document with audio URL
        document.audio_url = audio_url
        document.audio_key = processed_audio_key
        document.processing_status = 'completed'
        db.commit()
        logger.info(f"Document {document_id} processed successfully")
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        if document:
            document.processing_status = 'failed'
            document.processing_error = str(e)
            db.commit()
    finally:
        db.close()


def delete_document(db: Session, document_id: int, user_id: int) -> bool:
    """Delete document and associated files."""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Delete files from S3
        if document.file_key:
            s3_handler.delete_file(settings.S3_BUCKET_NAME, document.file_key)
        if document.audio_key:
            s3_handler.delete_file(settings.S3_BUCKET_NAME, document.audio_key)

        # Delete database record
        db.delete(document)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

