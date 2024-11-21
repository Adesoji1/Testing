from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks # type: ignore
import openai
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import io
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import time
import os
from tenacity import retry, wait_exponential, stop_after_attempt
from pydub import AudioSegment
from app.schemas.audiobook import AudioBookCreate
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from app.models import Document, User
from app.schemas.document import (
    DocumentCreate,
    DocumentFilter,
    DocumentUpdate,
    DocumentResponse,
    DocumentStats,
)
from sqlalchemy import func

from app.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.services.document_service import (
    create_document,
    get_documents,
    update_document,
    delete_document,
    process_document,
)
from app.services.audiobook_service import create_audiobook  # Import audiobook service
from app.schemas.audiobook import AudioBookCreate  
from app.utils.s3_utils import s3_handler
from app.services.tts_service import TTSService
from app.services.ocr_service import ocr_service
from app.services.rekognition_service import RekognitionService
from pydub.effects import normalize
import subprocess


tts_service = TTSService(region_name=settings.REGION_NAME)

# Initialize the Rekognition service
rekognition_service = RekognitionService(region_name=settings.REGION_NAME)



logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)


def map_language_code_to_supported(detected_language: str) -> str:
    """
    Map the detected language to a supported AWS Comprehend language code.
    This ensures compatibility with AWS Comprehend's supported language list.
    """
    supported_languages = {
        "en": "English",  # English
        "es": "Spanish",  # Spanish
        "fr": "French",  # French
        "de": "German",  # German
        "it": "Italian",  # Italian
        "pt": "Portugese",  # Portuguese
        "ar": "Arabic",  # Arabic
        "hi": "Hindi",  # Hindi
        "ja": "Japanese",  # Japanese
        "ko": "Korean",  # Korean
        "zh": "Simplified Chinese",  # Simplified Chinese
        "zh-TW": "Traditional Chinese",  # Traditional Chinese
        "nl" : "Dutch",
    }

    # If the language is unsupported, default to English
    return supported_languages.get(detected_language, "en")


def apply_immersive_effects(audio: AudioSegment) -> AudioSegment:
    """Apply immersive audio effects."""
    audio = normalize(audio)
    left = audio.pan(-0.5)
    right = audio.pan(0.5)
    return left.overlay(right)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    is_public: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        start_time = time.time()

        # Read the uploaded file content
        file_content = file.file.read()

        # Allowed content types
        ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain"]

        # Check file type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type for processing.",
            )

        # Generate the file key for S3
        file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

        # Upload the file to S3
        s3_url = s3_handler.upload_file(
            file_obj=io.BytesIO(file_content),
            bucket=settings.S3_BUCKET_NAME,
            key=file_key,
            content_type=file.content_type,
        )
        if not s3_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to S3",
            )

        # Create a database record for the document
        document_data = DocumentCreate(
            title=file.filename,
            author=user.username,
            file_type=file.content_type,
            file_key=file_key,
            url=s3_url,
            is_public=is_public,
        )
        document = create_document(
            db=db,
            document=document_data,
            user_id=user.id,
            file_key=file_key,
            file_size=len(file_content),
        )

        # Update processing status to "processing"
        document.processing_status = "processing"
        db.commit()

        # Start processing the document
        try:
            with ThreadPoolExecutor(max_workers=13) as executor:
                #
                # Determine file type and process accordingly
                if document.file_type == "application/pdf":
                    text, detected_language = ocr_service.extract_text_from_pdf(
                        bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
                    )
                elif document.file_type.startswith("image/"):
                    text, detected_language = ocr_service.extract_text_from_image(
                        bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
                    )
                    # Rekognition for tags
                    tags = rekognition_service.detect_labels(
                        bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
                    )
                    if isinstance(tags, str):
                        tags = tags.split(", ")
                    if not tags:
                        tags = ["No tags detected"]
                    document.tags = tags
                elif document.file_type == "text/plain":
                   text = file_content.decode("utf-8")
                   detected_language = "en"
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Unsupported file type for processing.",
                    )

                if not text.strip():
                    raise Exception("No text found in the document.")

                # Map detected language to full name
                full_language_name = map_language_code_to_supported(detected_language)
                document.detected_language = full_language_name

                # Generate description
                document.description = text[:200].strip()

                # Infer genre
                genre_keywords = {
                    "Fiction": ["story", "novel", "fiction", "tale", "narrative"],
                    "Technology": ["technology", "tech", "software", "hardware", "AI", "robotics"],
                    "Science": ["science", "experiment", "research", "physics", "chemistry", "biology"],
                    "Health/Medicine": ["health", "medicine", "wellness", "fitness", "medical", "therapy"],
                    "History": ["history", "historical", "ancient", "medieval", "war", "biography"],
                    "Environment/Nature": ["environment", "nature", "ecology", "climate", "wildlife"],
                    "Education": ["education", "teaching", "learning", "training", "academics", "study"],
                    "Business/Finance": ["profit", "loss", "business", "finance", "investment", "marketing", "economics"],
                    "Art/Culture": ["art", "culture", "painting", "sculpture", "music", "theater", "dance", "poetry"],
                    "Sports/Games": ["sports", "games", "athletics", "fitness", "competition", "team", "tournament"],
                    "Cover/Letter": ["Dear Hiring Team", "Hiring Manager", "application", "resume", "CV"],
                    "Travel/Adventure": ["travel", "adventure", "journey", "destination", "exploration", "trip"],
                    "Fantasy": ["fantasy", "magic", "myth", "legend", "wizard", "dragon", "epic"],
                    "Mystery/Thriller": ["mystery", "thriller", "detective", "crime", "suspense", "investigation"],
                    "Romance": ["romance", "love", "passion", "relationship", "heart", "affection"],
                    "Self-Help": ["self-help", "motivation", "personal development", "growth", "success", "habits"],
                    "Science Fiction": ["sci-fi", "space", "alien", "future", "technology", "robot"],
                    "Horror": ["horror", "scary", "ghost", "monster", "haunted", "fear"],
                    "Children": ["children", "kids", "fairy tale", "adventure", "learning", "nursery"],
                    "Comedy/Humor": ["comedy", "humor", "funny", "joke", "satire", "parody"],
                    "Religion/Spirituality": ["religion", "spirituality", "faith", "belief", "prayer", "philosophy"],
                    "Politics": ["politics", "government", "policy", "diplomacy", "elections", "law"],
                    "Cooking/Food": ["cooking", "food", "recipe", "culinary", "kitchen", "diet", "nutrition"],
                    "Travel Guides": ["travel", "destination", "guide", "itinerary", "vacation", "tour"],
                }

            
                genre = "Unknown"
                for key, keywords in genre_keywords.items():
                    if any(keyword in text.lower() for keyword in keywords):
                       genre = key
                       break
                document.genre = genre

                # Generate audio using Text-to-Speech
                max_length = 3000
                text_chunks = [text[i : i + max_length] for i in range(0, len(text), max_length)]
                audio_segments = []

                audio_chunks = list(
                    executor.map(
                        lambda chunk: tts_service.convert_text_to_speech(chunk, detected_language),
                        text_chunks,
                    )
                )
                for chunk_audio in audio_chunks:
                    audio_segment = AudioSegment.from_file(io.BytesIO(chunk_audio), format="mp3")
                    audio_segments.append(audio_segment)

                combined_audio = sum(audio_segments)

                # Calculate audio duration in hours and minutes
                duration_in_seconds = len(combined_audio) // 1000
                duration_in_minutes = duration_in_seconds // 60
                duration_in_hours = duration_in_minutes // 60
                formatted_duration = f"{duration_in_hours} hours {duration_in_minutes % 60} minutes"

                # Export processed audio to BytesIO
                audio_bytes_io = io.BytesIO()
                combined_audio.export(audio_bytes_io, format="mp3")
                audio_bytes_io.seek(0)

                # Upload processed audio to S3
                processed_audio_key = f"{settings.S3_FOLDER_NAME}/audio/{user.id}/{document.id}_processed.mp3"
                audio_url = s3_handler.upload_file(
                    file_obj=audio_bytes_io,
                    bucket=settings.S3_BUCKET_NAME,
                    key=processed_audio_key,
                    content_type="audio/mpeg",
                )
                document.audio_url = audio_url

                # Create audiobook record
                audiobook_data = AudioBookCreate(
                    title=document.title,
                    narrator="Generated Narrator",
                    duration=formatted_duration,
                    genre=genre,
                    publication_date=datetime.utcnow(),
                    author=document.author,
                    file_key=processed_audio_key,
                    url=audio_url,
                    is_dolby_atmos_supported=True,
                    document_id=document.id,
                )
                audiobook = create_audiobook(db=db, audiobook=audiobook_data)

                # Link the audiobook to the document
                document.audiobook = audiobook
                document.processing_status = "completed"
                db.commit()

                end_time = time.time()
                total_processing_time = end_time - start_time
                logger.info(f"Total processing time for document {document.id}: {total_processing_time:.2f} seconds")

                return document

        except Exception as processing_error:
            logger.error(f"Error processing document {document.id}: {str(processing_error)}")
            document.processing_status = "failed"
            document.processing_error = str(processing_error)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {str(processing_error)}",
            )

    except HTTPException as http_exc:
        logger.error(f"HTTP error uploading document: {str(http_exc.detail)}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document",
        )




# List Documents Endpoint

@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    status: Optional[str] = None,
    file_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of documents belonging to the current user.
    """
    try:
        filter_params = DocumentFilter(
            search=search,
            status=status,
            file_type=file_type,
            start_date=start_date,
            end_date=end_date
        )
        documents = get_documents(
            db=db,
            user_id=user.id,
            filter_params=filter_params,
            skip=skip,
            limit=limit
        )
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents",
        )

#This endpoint allows you to check the processing status of a specific document, including its audio_url if processing is complete.

@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve the processing status of a single document.

    This endpoint returns the document details, including the current
    `processing_status` (e.g., "pending", "completed", "failed") and the
    `audio_url` when available.
    - To learn more about the API, check the [documentation page](https://your-documentation-link)
    """
    try:
        # Query the database for the specified document
        document = db.query(Document).options(joinedload(Document.audiobook)).filter(
        # document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user.id
        ).first()

        # Raise an error if the document is not found
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Return the document details
        return document

    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document",
        )



# Update Document Endpoint
@router.put("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def update_document_endpoint(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing document's metadata.
    """
    try:
        document = update_document(
            db=db,
            document_id=document_id,
            user_id=user.id,
            update_data=document_update,
        )
        return document
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document",
        )

# Delete Document Endpoint
@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a document by its ID.
    """
    try:
        success = delete_document(db=db, document_id=document_id, user_id=user.id)
        if success:
            return {"detail": "Document deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )

# Get Document Statistics Endpoint
@router.get("/stats", response_model=DocumentStats)
async def get_document_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get statistics about the documents of the current user.
    """
    try:
        total_docs = db.query(Document).filter(Document.user_id == user.id).count()
        processed_docs = (
            db.query(Document)
            .filter(Document.user_id == user.id, Document.processing_status == "completed")
            .count()
        )
        failed_docs = (
            db.query(Document)
            .filter(Document.user_id == user.id, Document.processing_status == "failed")
            .count()
        )
        total_storage = (
            db.query(func.sum(Document.file_size))
            .filter(Document.user_id == user.id)
            .scalar()
            or 0
        )

        return DocumentStats(
            total_documents=total_docs,
            processed_documents=processed_docs,
            failed_documents=failed_docs,
            total_storage_used=total_storage / (1024 * 1024),  # Convert bytes to MB
        )
    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document statistics",
        )


@router.post("/multi-upload", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
def upload_documents(
    files: List[UploadFile] = File(..., description="Upload up to 5 documents", max_items=5),
    is_public: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    documents = []
    for file in files:
        try:
            # Read the uploaded file content
            file_content = file.file.read()

            # Allowed content types
            ALLOWED_CONTENT_TYPES = [
                'application/pdf',
                'image/png',
                'image/jpeg',
                'image/jpg',
                'text/plain',
            ]

            # Check file content type
            if file.content_type not in ALLOWED_CONTENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file.content_type}",
                )

            # Check file size limit
            if len(file_content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB",
                )

            # Generate the file key for S3
            file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

            # Upload the file to S3
            s3_url = s3_handler.upload_file(
                file_obj=io.BytesIO(file_content),
                bucket=settings.S3_BUCKET_NAME,
                key=file_key,
                content_type=file.content_type,
            )

            if not s3_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload file to S3",
                )

            # Create a database record for the document
            document_data = DocumentCreate(
                title=file.filename,
                author=user.username,
                file_type=file.content_type,
                file_key=file_key,
                url=s3_url,
                is_public=is_public,
            )
            document = create_document(
                db=db,
                document=document_data,
                user_id=user.id,
                file_key=file_key,
                file_size=len(file_content),
            )

            # Update processing status to "processing"
            document.processing_status = "processing"
            db.commit()

            start_time = time.time()

            # Process the document synchronously (OCR and TTS)
            try:
                # Extract text using OCR
                if document.file_type == "application/pdf":
                    text, detected_language = ocr_service.extract_text_from_pdf(
                        bucket_name=settings.S3_BUCKET_NAME,
                        file_key=document.file_key,
                    )
                elif document.file_type.startswith("image/"):
                    text, detected_language = ocr_service.extract_text_from_image(
                        bucket_name=settings.S3_BUCKET_NAME,
                        file_key=document.file_key,
                    )
                elif document.file_type == "text/plain":
                    text = file_content.decode('utf-8')
                    detected_language = 'en'  # Default or use language detection
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported file type: {document.file_type}",
                    )

                if not text.strip():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No text found in the document.",
                    )

                # Generate a description from the extracted text
                description_length = 200  # Adjust as needed
                description = text[:description_length].strip()
                document.description = description

                # Generate audio using TTS
                max_length = 3000
                text_chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
                audio_bytes_io = io.BytesIO()

                for chunk in text_chunks:
                    chunk_audio = tts_service.convert_text_to_speech(
                        chunk,
                        detected_language=detected_language,
                    )
                    audio_bytes_io.write(chunk_audio)

                audio_bytes_io.seek(0)  # Reset the cursor to the beginning

                # Record the end time
                end_time = time.time()
                processing_time = end_time - start_time

                # Log the processing time
                logger.info(f"Processing time for document {document.id}: {processing_time:.2f} seconds")

                # Upload the generated audio file to S3
                audio_key = f"{settings.S3_FOLDER_NAME}/audio/{user.id}/{document.id}.mp3"
                audio_url = s3_handler.upload_file(
                    file_obj=audio_bytes_io,
                    bucket=settings.S3_BUCKET_NAME,
                    key=audio_key,
                    content_type="audio/mpeg",
                )

                if not audio_url:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to upload audio file to S3",
                    )

                # Update the document with the generated audio URL
                document.audio_url = audio_url
                document.audio_key = audio_key
                document.processing_status = "completed"
                document.detected_language = detected_language
                db.commit()
                db.refresh(document)

            except Exception as processing_error:
                logger.error(f"Error processing document {document.id}: {str(processing_error)}")
                document.processing_status = "failed"
                document.processing_error = str(processing_error)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Document processing failed: {str(processing_error)}",
                )

            # Append the processed document to the list
            documents.append(document)

        except HTTPException as http_exc:
            logger.error(f"HTTP error uploading document {file.filename}: {str(http_exc.detail)}")
            db.rollback()
            raise http_exc
        except Exception as e:
            logger.error(f"Error uploading document {file.filename}: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload document {file.filename}",
            )

    return documents