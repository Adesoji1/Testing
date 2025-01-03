# #app/api/endpoints/user/documents.py
# from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks # type: ignore
# import openai
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from datetime import datetime
# import logging
# import io
# from io import BytesIO
# from concurrent.futures import ThreadPoolExecutor
# import time
# import os
# from tenacity import retry, wait_exponential, stop_after_attempt
# from pydub import AudioSegment
# from app.schemas.audiobook import AudioBookCreate
# from pydantic import BaseModel
# from sqlalchemy.orm import joinedload
# from app.models import Document, User
# from app.schemas.document import (
#     DocumentCreate,
#     DocumentFilter,
#     DocumentUpdate,
#     DocumentResponse,
#     DocumentStats,
# )
# from sqlalchemy import func

# from app.database import get_db
# from app.core.security import get_current_user
# from app.core.config import settings
# from app.services.document_service import (
#     create_document,
#     get_documents,
#     update_document,
#     delete_document,
#     process_document,
# )
# from app.services.audiobook_service import create_audiobook  # Import audiobook service
# from app.schemas.audiobook import AudioBookCreate  
# from app.utils.s3_utils import s3_handler
# from app.services.tts_service import TTSService
# from app.services.ocr_service import ocr_service
# from app.services.rekognition_service import RekognitionService
# from pydub.effects import normalize
# import subprocess


# tts_service = TTSService(region_name=settings.REGION_NAME)

# # Initialize the Rekognition service
# rekognition_service = RekognitionService(region_name=settings.REGION_NAME)



# logger = logging.getLogger(__name__)

# router = APIRouter(
#     prefix="/documents",
#     tags=["documents"],
#     responses={
#         400: {"description": "Bad Request"},
#         401: {"description": "Unauthorized"},
#         403: {"description": "Forbidden"},
#         404: {"description": "Not Found"},
#         500: {"description": "Internal Server Error"},
#     },
# )


# def map_language_code_to_supported(detected_language: str) -> str:
#     """
#     Map the detected language to a supported AWS Comprehend language code.
#     This ensures compatibility with AWS Comprehend's supported language list.
#     """
#     supported_languages = {
#         "en": "English",  # English
#         "es": "Spanish",  # Spanish
#         "fr": "French",  # French
#         "de": "German",  # German
#         "it": "Italian",  # Italian
#         "pt": "Portugese",  # Portuguese
#         "ar": "Arabic",  # Arabic
#         "hi": "Hindi",  # Hindi
#         "ja": "Japanese",  # Japanese
#         "ko": "Korean",  # Korean
#         "zh": "Simplified Chinese",  # Simplified Chinese
#         "zh-TW": "Traditional Chinese",  # Traditional Chinese
#         "nl" : "Dutch",
#     }

#     # If the language is unsupported, default to English
#     return supported_languages.get(detected_language, "en")


# def apply_immersive_effects(audio: AudioSegment) -> AudioSegment:
#     """Apply immersive audio effects."""
#     audio = normalize(audio)
#     left = audio.pan(-0.5)
#     right = audio.pan(0.5)
#     return left.overlay(right)


# @router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
# def upload_document(
#     file: UploadFile = File(...),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     try:
#         start_time = time.time()

#         # Read the uploaded file content
#         file_content = file.file.read()

#         # Allowed content types
#         ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain"]

#         # Check file type
#         if file.content_type not in ALLOWED_CONTENT_TYPES:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Unsupported file type for processing.",
#             )

#         # Generate the file key for S3
#         file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

#         # Upload the file to S3
#         s3_url = s3_handler.upload_file(
#             file_obj=io.BytesIO(file_content),
#             bucket=settings.S3_BUCKET_NAME,
#             key=file_key,
#             content_type=file.content_type,
#         )
#         if not s3_url:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload file to S3",
#             )

#         # Create a database record for the document
#         document_data = DocumentCreate(
#             title=file.filename,
#             author=user.username,
#             file_type=file.content_type,
#             file_key=file_key,
#             url=s3_url,
#             is_public=is_public,
#         )
#         document = create_document(
#             db=db,
#             document_data=document_data,
#             user_id=user.id,
#             file_key=file_key,
#             file_size=len(file_content),
#         )

#         # Update processing status to "processing"
#         document.processing_status = "processing"
#         db.commit()

#         # Start processing the document
#         try:
#             with ThreadPoolExecutor(max_workers=18) as executor:
#                 #
#                 # Determine file type and process accordingly
#                 if document.file_type == "application/pdf":
#                     text, detected_language = ocr_service.extract_text_from_pdf(
#                         bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
#                     )
#                 elif document.file_type.startswith("image/"):
#                     text, detected_language = ocr_service.extract_text_from_image(
#                         bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
#                     )
#                     # Rekognition for tags
#                     tags = rekognition_service.detect_labels(
#                         bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
#                     )
#                     if isinstance(tags, str):
#                         tags = tags.split(", ")
#                     if not tags:
#                         tags = ["No tags detected"]
#                     document.tags = tags
#                 elif document.file_type == "text/plain":
#                    text = file_content.decode("utf-8")
#                    detected_language = "en"
#                 else:
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail="Unsupported file type for processing.",
#                     )

#                 if not text.strip():
#                     raise Exception("No text found in the document.")

#                 # Map detected language to full name
#                 full_language_name = map_language_code_to_supported(detected_language)
#                 document.detected_language = full_language_name

#                 # Generate description
#                 document.description = text[:200].strip()

#                 # Infer genre
#                 genre_keywords = {
#                     "Fiction": ["story", "novel", "fiction", "tale", "narrative"],
#                     "Technology": ["technology", "tech", "software", "hardware", "AI", "robotics"],
#                     "Science": ["science", "experiment", "research", "physics", "chemistry", "biology"],
#                     "Health/Medicine": ["health", "medicine", "wellness", "fitness", "medical", "therapy"],
#                     "History": ["history", "historical", "ancient", "medieval", "war", "biography"],
#                     "Environment/Nature": ["environment", "nature", "ecology", "climate", "wildlife"],
#                     "Education": ["education", "teaching", "learning", "training", "academics", "study"],
#                     "Business/Finance": ["profit", "loss", "business", "finance", "investment", "marketing", "economics"],
#                     "Art/Culture": ["art", "culture", "painting", "sculpture", "music", "theater", "dance", "poetry"],
#                     "Sports/Games": ["sports", "games", "athletics", "fitness", "competition", "team", "tournament"],
#                     "Cover/Letter": ["Dear Hiring Team", "Hiring Manager", "application", "resume", "CV"],
#                     "Travel/Adventure": ["travel", "adventure", "journey", "destination", "exploration", "trip"],
#                     "Fantasy": ["fantasy", "magic", "myth", "legend", "wizard", "dragon", "epic"],
#                     "Mystery/Thriller": ["mystery", "thriller", "detective", "crime", "suspense", "investigation"],
#                     "Romance": ["romance", "love", "passion", "relationship", "heart", "affection"],
#                     "Self-Help": ["self-help", "motivation", "personal development", "growth", "success", "habits"],
#                     "Science Fiction": ["sci-fi", "space", "alien", "future", "technology", "robot"],
#                     "Horror": ["horror", "scary", "ghost", "monster", "haunted", "fear"],
#                     "Children": ["children", "kids", "fairy tale", "adventure", "learning", "nursery"],
#                     "Comedy/Humor": ["comedy", "humor", "funny", "joke", "satire", "parody"],
#                     "Religion/Spirituality": ["religion", "spirituality", "faith", "belief", "prayer", "philosophy"],
#                     "Politics": ["politics", "government", "policy", "diplomacy", "elections", "law"],
#                     "Cooking/Food": ["cooking", "food", "recipe", "culinary", "kitchen", "diet", "nutrition"],
#                     "Travel Guides": ["travel", "destination", "guide", "itinerary", "vacation", "tour"],
#                 }

            
#                 genre = "Unknown"
#                 for key, keywords in genre_keywords.items():
#                     if any(keyword in text.lower() for keyword in keywords):
#                        genre = key
#                        break
#                 document.genre = genre

#                 # Generate audio using Text-to-Speech
#                 max_length = 3000
#                 text_chunks = [text[i : i + max_length] for i in range(0, len(text), max_length)]
#                 audio_segments = []

#                 audio_chunks = list(
#                     executor.map(
#                         lambda chunk: tts_service.convert_text_to_speech(chunk, detected_language),
#                         text_chunks,
#                     )
#                 )
#                 for chunk_audio in audio_chunks:
#                     audio_segment = AudioSegment.from_file(io.BytesIO(chunk_audio), format="mp3")
#                     audio_segments.append(audio_segment)

#                 combined_audio = sum(audio_segments)

#                 # Calculate audio duration in hours and minutes
#                 duration_in_seconds = len(combined_audio) // 1000
#                 duration_in_minutes = duration_in_seconds // 60
#                 duration_in_hours = duration_in_minutes // 60
#                 formatted_duration = f"{duration_in_hours} hours {duration_in_minutes % 60} minutes"

#                 # Export processed audio to BytesIO
#                 audio_bytes_io = io.BytesIO()
#                 combined_audio.export(audio_bytes_io, format="mp3")
#                 audio_bytes_io.seek(0)

#                 # Upload processed audio to S3
#                 processed_audio_key = f"{settings.S3_FOLDER_NAME}/audio/{user.id}/{document.id}_processed.mp3"
#                 audio_url = s3_handler.upload_file(
#                     file_obj=audio_bytes_io,
#                     bucket=settings.S3_BUCKET_NAME,
#                     key=processed_audio_key,
#                     content_type="audio/mpeg",
#                 )
#                 document.audio_url = audio_url

#                 # Create audiobook record
#                 audiobook_data = AudioBookCreate(
#                     title=document.title,
#                     narrator="Generated Narrator",
#                     duration=formatted_duration,
#                     genre=genre,
#                     publication_date=datetime.utcnow(),
#                     author=document.author,
#                     file_key=processed_audio_key,
#                     url=audio_url,
#                     is_dolby_atmos_supported=True,
#                     document_id=document.id,
#                 )
#                 audiobook = create_audiobook(db=db, audiobook=audiobook_data)

#                 # Link the audiobook to the document
#                 document.audiobook = audiobook
#                 document.processing_status = "completed"
#                 db.commit()

#                 end_time = time.time()
#                 total_processing_time = end_time - start_time
#                 logger.info(f"Total processing time for document {document.id}: {total_processing_time:.2f} seconds")

#                 return document

#         except Exception as processing_error:
#             logger.error(f"Error processing document {document.id}: {str(processing_error)}")
#             document.processing_status = "failed"
#             document.processing_error = str(processing_error)
#             db.commit()
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Document processing failed: {str(processing_error)}",
#             )

#     except HTTPException as http_exc:
#         logger.error(f"HTTP error uploading document: {str(http_exc.detail)}")
#         raise http_exc
#     except Exception as e:
#         logger.error(f"Error uploading document: {str(e)}")
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to upload document",
#         )




# # List Documents Endpoint

# @router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
# async def list_documents(
#     skip: int = 0,
#     limit: int = 10,
#     search: Optional[str] = None,
#     status: Optional[str] = None,
#     file_type: Optional[str] = None,
#     start_date: Optional[datetime] = None,
#     end_date: Optional[datetime] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Retrieve a list of documents belonging to the current user.
#     """
#     try:
#         filter_params = DocumentFilter(
#             search=search,
#             status=status,
#             file_type=file_type,
#             start_date=start_date,
#             end_date=end_date
#         )
#         documents = get_documents(
#             db=db,
#             user_id=user.id,
#             filter_params=filter_params,
#             skip=skip,
#             limit=limit
#         )
#         return documents
#     except Exception as e:
#         logger.error(f"Error listing documents: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve documents",
#         )

# #This endpoint allows you to check the processing status of a specific document, including its audio_url if processing is complete.

# @router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
# def get_document_status(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Retrieve the processing status of a single document.

#     This endpoint returns the document details, including the current
#     `processing_status` (e.g., "pending", "completed", "failed") and the
#     `audio_url` when available.
#     - To learn more about the API, check the [documentation page](https://your-documentation-link)
#     """
#     try:
#         # Query the database for the specified document
#         document = db.query(Document).options(joinedload(Document.audiobook)).filter(
#         # document = db.query(Document).filter(
#             Document.id == document_id,
#             Document.user_id == user.id
#         ).first()

#         # Raise an error if the document is not found
#         if not document:
#             raise HTTPException(status_code=404, detail="Document not found")

#         # Return the document details
#         return document

#     except Exception as e:
#         logger.error(f"Error retrieving document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document",
#         )



# # Update Document Endpoint
# @router.put("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
# async def update_document_endpoint(
#     document_id: int,
#     document_update: DocumentUpdate,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Update an existing document's metadata.
#     """
#     try:
#         document = update_document(
#             db=db,
#             document_id=document_id,
#             user_id=user.id,
#             update_data=document_update,
#         )
#         return document
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error updating document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update document",
#         )

# # Delete Document Endpoint
# @router.delete("/{document_id}", status_code=status.HTTP_200_OK)
# async def delete_document_endpoint(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Delete a document by its ID.
#     """
#     try:
#         success = delete_document(db=db, document_id=document_id, user_id=user.id)
#         if success:
#             return {"detail": "Document deleted successfully"}
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Document not found",
#             )
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error deleting document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to delete document",
#         )

# # Get Document Statistics Endpoint
# @router.get("/stats", response_model=DocumentStats)
# async def get_document_stats(
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Get statistics about the documents of the current user.
#     """
#     try:
#         total_docs = db.query(Document).filter(Document.user_id == user.id).count()
#         processed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "completed")
#             .count()
#         )
#         failed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "failed")
#             .count()
#         )
#         total_storage = (
#             db.query(func.sum(Document.file_size))
#             .filter(Document.user_id == user.id)
#             .scalar()
#             or 0
#         )

#         return DocumentStats(
#             total_documents=total_docs,
#             processed_documents=processed_docs,
#             failed_documents=failed_docs,
#             total_storage_used=total_storage / (1024 * 1024),  # Convert bytes to MB
#         )
#     except Exception as e:
#         logger.error(f"Error getting document stats: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document statistics",
#         )


# @router.post("/multi-upload", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
# def upload_documents(
#     files: List[UploadFile] = File(..., description="Upload up to 5 documents", max_items=5),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     documents = []
#     for file in files:
#         try:
#             # Read the uploaded file content
#             file_content = file.file.read()

#             # Allowed content types
#             ALLOWED_CONTENT_TYPES = [
#                 'application/pdf',
#                 'image/png',
#                 'image/jpeg',
#                 'image/jpg',
#                 'text/plain',
#             ]

#             # Check file content type
#             if file.content_type not in ALLOWED_CONTENT_TYPES:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Unsupported file type: {file.content_type}",
#                 )

#             # Check file size limit
#             if len(file_content) > settings.MAX_UPLOAD_SIZE:
#                 raise HTTPException(
#                     status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                     detail=f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB",
#                 )

#             # Generate the file key for S3
#             file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

#             # Upload the file to S3
#             s3_url = s3_handler.upload_file(
#                 file_obj=io.BytesIO(file_content),
#                 bucket=settings.S3_BUCKET_NAME,
#                 key=file_key,
#                 content_type=file.content_type,
#             )

#             if not s3_url:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Failed to upload file to S3",
#                 )

#             # Create a database record for the document
#             document_data = DocumentCreate(
#                 title=file.filename,
#                 author=user.username,
#                 file_type=file.content_type,
#                 file_key=file_key,
#                 url=s3_url,
#                 is_public=is_public,
#             )
#             document = create_document(
#                 db=db,
#                 document_data=document_data,
#                 user_id=user.id,
#                 file_key=file_key,
#                 file_size=len(file_content),
#             )

#             # Update processing status to "processing"
#             document.processing_status = "processing"
#             db.commit()

#             start_time = time.time()

#             # Process the document synchronously (OCR and TTS)
#             try:
#                 # Extract text using OCR
#                 if document.file_type == "application/pdf":
#                     text, detected_language = ocr_service.extract_text_from_pdf(
#                         bucket_name=settings.S3_BUCKET_NAME,
#                         file_key=document.file_key,
#                     )
#                 elif document.file_type.startswith("image/"):
#                     text, detected_language = ocr_service.extract_text_from_image(
#                         bucket_name=settings.S3_BUCKET_NAME,
#                         file_key=document.file_key,
#                     )
#                 elif document.file_type == "text/plain":
#                     text = file_content.decode('utf-8')
#                     detected_language = 'en'  # Default or use language detection
#                 else:
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail=f"Unsupported file type: {document.file_type}",
#                     )

#                 if not text.strip():
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail="No text found in the document.",
#                     )

#                 # Generate a description from the extracted text
#                 description_length = 200  # Adjust as needed
#                 description = text[:description_length].strip()
#                 document.description = description

#                 # Generate audio using TTS
#                 max_length = 3000
#                 text_chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
#                 audio_bytes_io = io.BytesIO()

#                 for chunk in text_chunks:
#                     chunk_audio = tts_service.convert_text_to_speech(
#                         chunk,
#                         detected_language=detected_language,
#                     )
#                     audio_bytes_io.write(chunk_audio)

#                 audio_bytes_io.seek(0)  # Reset the cursor to the beginning

#                 # Record the end time
#                 end_time = time.time()
#                 processing_time = end_time - start_time

#                 # Log the processing time
#                 logger.info(f"Processing time for document {document.id}: {processing_time:.2f} seconds")

#                 # Upload the generated audio file to S3
#                 audio_key = f"{settings.S3_FOLDER_NAME}/audio/{user.id}/{document.id}.mp3"
#                 audio_url = s3_handler.upload_file(
#                     file_obj=audio_bytes_io,
#                     bucket=settings.S3_BUCKET_NAME,
#                     key=audio_key,
#                     content_type="audio/mpeg",
#                 )

#                 if not audio_url:
#                     raise HTTPException(
#                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                         detail="Failed to upload audio file to S3",
#                     )

#                 # Update the document with the generated audio URL
#                 document.audio_url = audio_url
#                 document.audio_key = audio_key
#                 document.processing_status = "completed"
#                 document.detected_language = detected_language
#                 db.commit()
#                 db.refresh(document)

#             except Exception as processing_error:
#                 logger.error(f"Error processing document {document.id}: {str(processing_error)}")
#                 document.processing_status = "failed"
#                 document.processing_error = str(processing_error)
#                 db.commit()
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Document processing failed: {str(processing_error)}",
#                 )

#             # Append the processed document to the list
#             documents.append(document)

#         except HTTPException as http_exc:
#             logger.error(f"HTTP error uploading document {file.filename}: {str(http_exc.detail)}")
#             db.rollback()
#             raise http_exc
#         except Exception as e:
#             logger.error(f"Error uploading document {file.filename}: {str(e)}")
#             db.rollback()
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Failed to upload document {file.filename}",
#             )

#     return documents



# app/api/endpoints/user/documents.py

# from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
# from sqlalchemy.orm import Session, joinedload
# from typing import List, Optional
# from datetime import datetime
# import logging
# import io
# from concurrent.futures import ThreadPoolExecutor
# import time

# from app.schemas.audiobook import AudioBookCreate
# from app.schemas.document import (
#     DocumentCreate,
#     DocumentFilter,
#     DocumentUpdate,
#     DocumentResponse,
#     DocumentStats,
# )

# from app.models import Document, User
# from app.database import get_db
# from app.core.security import get_current_user
# from app.core.config import settings
# from app.services.document_service import (
#     create_document,
#     get_documents,
#     update_document,
#     delete_document,
#     process_document,
# )
# from app.services.audiobook_service import create_audiobook  # Import audiobook service
# from app.utils.s3_utils import s3_handler
# from app.services.tts_service import tts_service
# from app.services.ocr_service import ocr_service
# from app.services.rekognition_service import RekognitionService
# from pydub import AudioSegment
# from pydub.effects import normalize
# from fastapi import BackgroundTasks

# # Initialize the Rekognition service
# rekognition_service = RekognitionService(region_name=settings.REGION_NAME)

# logger = logging.getLogger(__name__)

# router = APIRouter(
#     prefix="/documents",
#     tags=["documents"],
#     responses={
#         400: {"description": "Bad Request"},
#         401: {"description": "Unauthorized"},
#         403: {"description": "Forbidden"},
#         404: {"description": "Not Found"},
#         500: {"description": "Internal Server Error"},
#     },
# )


# def map_language_code_to_supported(detected_language: str) -> str:
#     """
#     Map the detected language code to its full language name.
#     This ensures consistency in language representation.
#     """
#     supported_languages = {
#         "en": "English",
#         "es": "Spanish",
#         "fr": "French",
#         "de": "German",
#         "it": "Italian",
#         "pt": "Portuguese",
#         "ar": "Arabic",
#         "hi": "Hindi",
#         "ja": "Japanese",
#         "ko": "Korean",
#         "zh": "Simplified Chinese",
#         "zh-TW": "Traditional Chinese",
#         "nl": "Dutch",
#         # Add more mappings as needed
#     }

#     # If the language is unsupported, default to English
#     return supported_languages.get(detected_language, "English")


# def add_delay(audio: AudioSegment, delay_ms: int = 50, attenuation_db: float = 10.0) -> AudioSegment:
#     """
#     Adds a delayed and attenuated copy of the audio to itself to simulate reverb.

#     :param audio: Original AudioSegment.
#     :param delay_ms: Delay in milliseconds.
#     :param attenuation_db: Attenuation in decibels for the delayed copy.
#     :return: AudioSegment with delay effect applied.
#     """
#     # Create a silent audio segment for the delay
#     silent_segment = AudioSegment.silent(duration=delay_ms)

#     # Create the delayed copy
#     delayed_copy = silent_segment + audio

#     # Attenuate the delayed copy
#     delayed_copy = delayed_copy - attenuation_db

#     # Overlay the delayed copy onto the original audio
#     return audio.overlay(delayed_copy)




# def apply_immersive_effects(audio: AudioSegment) -> AudioSegment:
#     """
#     Apply immersive audio effects including stereo widening and subtle reverb.
#     """
#     # Normalize audio volume
#     audio = normalize(audio)

#     # Stereo widening by slightly panning the audio
#     left = audio.pan(-0.3)   # Pan 30% to the left
#     right = audio.pan(0.3)   # Pan 30% to the right

#     # Combine left and right to create a wider stereo effect
#     immersive_audio = left.overlay(right)

#     # Add a subtle reverb effect by adding delay
#     immersive_audio = add_delay(immersive_audio, delay_ms=50, attenuation_db=10)

#     # Normalize again after effects
#     immersive_audio = normalize(immersive_audio)

#     return immersive_audio




# @router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
# def upload_document(
#     file: UploadFile = File(...),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Upload a document, perform OCR and TTS processing, and return the document details.
#     """
#     try:
#         start_time = time.time()

#         # Read the uploaded file content
#         file_content = file.file.read()

#         # Allowed content types
#         ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain"]

#         # Check file type
#         if file.content_type not in ALLOWED_CONTENT_TYPES:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Unsupported file type for processing.",
#             )

#         # # Generate the file key for S3
#         # file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"
        
#         # Generate the file key for S3 with timestamp to ensure uniqueness
#         timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
#         file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{timestamp}_{file.filename}"
#         # Upload the file to S3
#         s3_url = s3_handler.upload_file(
#             file_obj=io.BytesIO(file_content),
#             bucket=settings.S3_BUCKET_NAME,
#             key=file_key,
#             content_type=file.content_type,
#         )
#         if not s3_url:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload file to S3",
#             )

#         # Create a database record for the document
#         document_data = DocumentCreate(
#             title=file.filename,
#             author=user.username,
#             file_type=file.content_type,
#             file_key=file_key,
#             url=s3_url,
#             is_public=is_public,
#         )
#         document = create_document(
#             db=db,
#             document_data=document_data,
#             user_id=user.id,
#             file_key=file_key,
#             file_size=len(file_content),
#         )

#         # Update processing status to "processing"
#         document.processing_status = "processing"
#         db.commit()

#         # Start processing the document
#         try:
#             # Start timing the processing
#             processing_start_time = time.time()

#             # Extract text and detect language
#             if document.file_type == "application/pdf":
#                 text, detected_language = ocr_service.extract_text_from_pdf(
#                     bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
#                 )
#             elif document.file_type.startswith("image/"):
#                 text, detected_language = ocr_service.extract_text_from_image(
#                     bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
#                 )
#                 # Rekognition for tags
#                 tags = rekognition_service.detect_labels(
#                     bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
#                 )
#                 if isinstance(tags, str):
#                     tags = tags.split(", ")
#                 if not tags:
#                     tags = ["No tags detected"]
#                 document.tags = tags
#             elif document.file_type == "text/plain":
#                 text = file_content.decode("utf-8")
#                 detected_language = "en"  # Default or use language detection
#             else:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Unsupported file type for processing.",
#                 )

#             if not text.strip():
#                 raise Exception("No text found in the document.")

#             # Map detected language to full name
#             full_language_name = map_language_code_to_supported(detected_language)
#             document.detected_language = full_language_name

#             # Generate description
#             document.description = text[:200].strip()

#             # Infer genre
#             genre_keywords = {
#                 "Fiction": ["story", "novel", "fiction", "tale", "narrative"],
#                 "Technology": ["technology", "tech", "software", "hardware", "AI", "robotics"],
#                 "Science": ["science", "experiment", "research", "physics", "chemistry", "biology"],
#                 "Health/Medicine": ["health", "medicine", "wellness", "fitness", "medical", "therapy"],
#                 "History": ["history", "historical", "ancient", "medieval", "war", "biography"],
#                 "Environment/Nature": ["environment", "nature", "ecology", "climate", "wildlife"],
#                 "Education": ["education", "teaching", "learning", "training", "academics", "study"],
#                 "Business/Finance": ["profit", "loss", "business", "finance", "investment", "marketing", "economics"],
#                 "Art/Culture": ["art", "culture", "painting", "sculpture", "music", "theater", "dance", "poetry"],
#                 "Sports/Games": ["sports", "games", "athletics", "fitness", "competition", "team", "tournament"],
#                 "Cover/Letter": ["dear hiring team", "hiring manager", "application", "resume", "cv"],
#                 "Travel/Adventure": ["travel", "adventure", "journey", "destination", "exploration", "trip"],
#                 "Fantasy": ["fantasy", "magic", "myth", "legend", "wizard", "dragon", "epic"],
#                 "Mystery/Thriller": ["mystery", "thriller", "detective", "crime", "suspense", "investigation"],
#                 "Romance": ["romance", "love", "passion", "relationship", "heart", "affection"],
#                 "Self-Help": ["self-help", "motivation", "personal development", "growth", "success", "habits"],
#                 "Science Fiction": ["sci-fi", "space", "alien", "future", "technology", "robot"],
#                 "Horror": ["horror", "scary", "ghost", "monster", "haunted", "fear"],
#                 "Children": ["children", "kids", "fairy tale", "adventure", "learning", "nursery"],
#                 "Comedy/Humor": ["comedy", "humor", "funny", "joke", "satire", "parody"],
#                 "Religion/Spirituality": ["religion", "spirituality", "faith", "belief", "prayer", "philosophy"],
#                 "Politics": ["politics", "government", "policy", "diplomacy", "elections", "law"],
#                 "Cooking/Food": ["cooking", "food", "recipe", "culinary", "kitchen", "diet", "nutrition"],
#                 "Travel Guides": ["travel", "destination", "guide", "itinerary", "vacation", "tour"],
#             }

#             genre = "Unknown"
#             for key, keywords in genre_keywords.items():
#                 if any(keyword in text.lower() for keyword in keywords):
#                     genre = key
#                     break
#             document.genre = genre

#             # Generate audio using Text-to-Speech
#             max_length = 3000  # Increased chunk size for fewer chunks
#             text_chunks = [text[i : i + max_length] for i in range(0, len(text), max_length)]
#             audio_segments = []

#             logger.info(f"Processing {len(text_chunks)} text chunks for TTS.")

#             # Optimize the number of workers based on chunks
#             max_workers = min(12, len(text_chunks)) if len(text_chunks) > 0 else 1

#             with ThreadPoolExecutor(max_workers=max_workers) as executor:
#                 audio_chunks = list(
#                     executor.map(
#                         lambda chunk: tts_service.convert_text_to_speech(chunk, detected_language),
#                         text_chunks,
#                     )
#                 )

#             logger.info("Completed TTS conversion for all chunks.")

#             for chunk_audio in audio_chunks:
#                 audio_segment = AudioSegment.from_file(io.BytesIO(chunk_audio), format="mp3")
#                 audio_segments.append(audio_segment)

#             # Combine all audio segments
#             combined_audio = AudioSegment.empty()
#             for segment in audio_segments:
#                 combined_audio += segment
#             # combined_audio = sum(audio_segments)

#             # Apply immersive audio effects
#             immersive_audio = apply_immersive_effects(combined_audio)

#             # Calculate audio duration in hours and minutes
#             duration_in_seconds = len(immersive_audio) / 1000  # pydub works in milliseconds
#             duration_in_minutes = duration_in_seconds // 60
#             duration_in_hours = duration_in_minutes // 60
#             formatted_duration = f"{int(duration_in_hours)} hours {int(duration_in_minutes % 60)} minutes"

#             # Export processed audio to BytesIO
#             audio_bytes_io = io.BytesIO()
#             immersive_audio.export(audio_bytes_io, format="mp3", bitrate="128k")
#             audio_bytes_io.seek(0)

#             # Upload processed audio to S3
#             processed_audio_key = f"{settings.S3_FOLDER_NAME}/audio/{user.id}/{document.id}_processed.mp3"
#             audio_url = s3_handler.upload_file(
#                 file_obj=audio_bytes_io,
#                 bucket=settings.S3_BUCKET_NAME,
#                 key=processed_audio_key,
#                 content_type="audio/mpeg",
#             )
#             document.audio_url = audio_url

#             # Create audiobook record
#             audiobook_data = AudioBookCreate(
#                 title=document.title,
#                 narrator="Generated Narrator",
#                 duration=formatted_duration,
#                 genre=genre,
#                 publication_date=datetime.utcnow(),
#                 author=document.author,
#                 file_key=processed_audio_key,
#                 url=audio_url,
#                 is_dolby_atmos_supported=True,
#                 document_id=document.id,
#             )
#             audiobook = create_audiobook(db=db, audiobook=audiobook_data)

#             # Link the audiobook to the document
#             document.audiobook = audiobook
#             document.processing_status = "completed"
#             db.commit()

#             # Record the end time and calculate total processing time
#             end_time = time.time()
#             total_processing_time = end_time - start_time
#             logger.info(f"Total processing time for document {document.id}: {total_processing_time:.2f} seconds")

#             # Ensure processing time is under 60 seconds
#             if total_processing_time > 60:
#                 logger.warning(f"Processing time exceeded 60 seconds for document {document.id}: {total_processing_time:.2f} seconds")

#             return document

#         except Exception as processing_error:
#             logger.error(f"Error processing document {document.id}: {str(processing_error)}")
#             document.processing_status = "failed"
#             document.processing_error = str(processing_error)
#             db.commit()
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Document processing failed: {str(processing_error)}",
#             )

#     except HTTPException as http_exc:
#         logger.error(f"HTTP error uploading document: {str(http_exc.detail)}")
#         raise http_exc
#     except Exception as e:
#         logger.error(f"Error uploading document: {str(e)}")
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to upload document",
#         )


# # List Documents Endpoint

# @router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
# async def list_documents(
#     skip: int = 0,
#     limit: int = 10,
#     search: Optional[str] = None,
#     status: Optional[str] = None,
#     file_type: Optional[str] = None,
#     start_date: Optional[datetime] = None,
#     end_date: Optional[datetime] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Retrieve a list of documents belonging to the current user.
#     """
#     try:
#         filter_params = DocumentFilter(
#             search=search,
#             status=status,
#             file_type=file_type,
#             start_date=start_date,
#             end_date=end_date
#         )
#         documents = get_documents(
#             db=db,
#             user_id=user.id,
#             filter_params=filter_params,
#             skip=skip,
#             limit=limit
#         )
#         return documents
#     except Exception as e:
#         logger.error(f"Error listing documents: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve documents",
#         )


# # Get Document Status Endpoint

# @router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
# def get_document_status(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Retrieve the processing status of a single document.

#     This endpoint returns the document details, including the current
#     `processing_status` (e.g., "pending", "completed", "failed") and the
#     `audio_url` when available.
#     - To learn more about the API, check the [documentation page](https://your-documentation-link)
#     """
#     try:
#         # Query the database for the specified document
#         document = db.query(Document).options(joinedload(Document.audiobook)).filter(
#             Document.id == document_id,
#             Document.user_id == user.id
#         ).first()

#         # Raise an error if the document is not found
#         if not document:
#             raise HTTPException(status_code=404, detail="Document not found")

#         # Return the document details
#         return document

#     except Exception as e:
#         logger.error(f"Error retrieving document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document",
#         )


# # Update Document Endpoint

# @router.put("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
# async def update_document_endpoint(
#     document_id: int,
#     document_update: DocumentUpdate,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Update an existing document's metadata.
#     """
#     try:
#         document = update_document(
#             db=db,
#             document_id=document_id,
#             user_id=user.id,
#             update_data=document_update,
#         )
#         return document
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error updating document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update document",
#         )


# # Delete Document Endpoint

# @router.delete("/{document_id}", status_code=status.HTTP_200_OK)
# async def delete_document_endpoint(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Delete a document by its ID.
#     """
#     try:
#         success = delete_document(db=db, document_id=document_id, user_id=user.id)
#         if success:
#             return {"detail": "Document deleted successfully"}
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Document not found",
#             )
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error deleting document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to delete document",
#         )


# # Get Document Statistics Endpoint

# @router.get("/stats", response_model=DocumentStats)
# async def get_document_stats(
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Get statistics about the documents of the current user.
#     """
#     try:
#         total_docs = db.query(Document).filter(Document.user_id == user.id).count()
#         processed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "completed")
#             .count()
#         )
#         failed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "failed")
#             .count()
#         )
#         total_storage = (
#             db.query(func.sum(Document.file_size))
#             .filter(Document.user_id == user.id)
#             .scalar()
#             or 0
#         )

#         return DocumentStats(
#             total_documents=total_docs,
#             processed_documents=processed_docs,
#             failed_documents=failed_docs,
#             total_storage_used=total_storage / (1024 * 1024),  # Convert bytes to MB
#         )
#     except Exception as e:
#         logger.error(f"Error getting document stats: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document statistics",
#         )


# # Multi-Upload Documents Endpoint

# @router.post("/multi-upload", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
# def upload_documents(
#     files: List[UploadFile] = File(..., description="Upload up to 5 documents", max_items=5),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Upload multiple documents, perform OCR and TTS processing, and return the document details.
#     """
#     documents = []
#     for file in files:
#         try:
#             # Start timing the upload and processing
#             start_time = time.time()

#             # Read the uploaded file content
#             file_content = file.file.read()

#             # Allowed content types
#             ALLOWED_CONTENT_TYPES = [
#                 'application/pdf',
#                 'image/png',
#                 'image/jpeg',
#                 'image/jpg',
#                 'text/plain',
#             ]

#             # Check file content type
#             if file.content_type not in ALLOWED_CONTENT_TYPES:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Unsupported file type: {file.content_type}",
#                 )

#             # Check file size limit
#             if len(file_content) > settings.MAX_UPLOAD_SIZE:
#                 raise HTTPException(
#                     status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                     detail=f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB",
#                 )

#             # Generate the file key for S3
#             file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

#             # Upload the file to S3
#             s3_url = s3_handler.upload_file(
#                 file_obj=io.BytesIO(file_content),
#                 bucket=settings.S3_BUCKET_NAME,
#                 key=file_key,
#                 content_type=file.content_type,
#             )

#             if not s3_url:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Failed to upload file to S3",
#                 )

#             # Create a database record for the document
#             document_data = DocumentCreate(
#                 title=file.filename,
#                 author=user.username,
#                 file_type=file.content_type,
#                 file_key=file_key,
#                 url=s3_url,
#                 is_public=is_public,
#             )
#             document = create_document(
#                 db=db,
#                 document_data=document_data,
#                 user_id=user.id,
#                 file_key=file_key,
#                 file_size=len(file_content),
#             )

#             # Update processing status to "processing"
#             document.processing_status = "processing"
#             db.commit()

#             # Process the document
#             try:
#                 # Start timing the processing
#                 processing_start_time = time.time()

#                 # Extract text and detect language
#                 if document.file_type == "application/pdf":
#                     text, detected_language = ocr_service.extract_text_from_pdf(
#                         bucket_name=settings.S3_BUCKET_NAME,
#                         file_key=document.file_key,
#                     )
#                 elif document.file_type.startswith("image/"):
#                     text, detected_language = ocr_service.extract_text_from_image(
#                         bucket_name=settings.S3_BUCKET_NAME,
#                         file_key=document.file_key,
#                     )
#                     # Rekognition for tags
#                     tags = rekognition_service.detect_labels(
#                         bucket_name=settings.S3_BUCKET_NAME, file_key=document.file_key
#                     )
#                     if isinstance(tags, str):
#                         tags = tags.split(", ")
#                     if not tags:
#                         tags = ["No tags detected"]
#                     document.tags = tags
#                 elif document.file_type == "text/plain":
#                     text = file_content.decode('utf-8')
#                     detected_language = 'en'  # Default or use language detection
#                 else:
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail=f"Unsupported file type: {document.file_type}",
#                     )

#                 if not text.strip():
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail="No text found in the document.",
#                     )

#                 # Map detected language to full name
#                 full_language_name = map_language_code_to_supported(detected_language)
#                 document.detected_language = full_language_name

#                 # Generate description
#                 document.description = text[:200].strip()

#                 # Infer genre
#                 genre_keywords = {
#                     "Fiction": ["story", "novel", "fiction", "tale", "narrative"],
#                     "Technology": ["technology", "tech", "software", "hardware", "AI", "robotics"],
#                     "Science": ["science", "experiment", "research", "physics", "chemistry", "biology"],
#                     "Health/Medicine": ["health", "medicine", "wellness", "fitness", "medical", "therapy"],
#                     "History": ["history", "historical", "ancient", "medieval", "war", "biography"],
#                     "Environment/Nature": ["environment", "nature", "ecology", "climate", "wildlife"],
#                     "Education": ["education", "teaching", "learning", "training", "academics", "study"],
#                     "Business/Finance": ["profit", "loss", "business", "finance", "investment", "marketing", "economics"],
#                     "Art/Culture": ["art", "culture", "painting", "sculpture", "music", "theater", "dance", "poetry"],
#                     "Sports/Games": ["sports", "games", "athletics", "fitness", "competition", "team", "tournament"],
#                     "Cover/Letter": ["dear hiring team", "hiring manager", "application", "resume", "cv"],
#                     "Travel/Adventure": ["travel", "adventure", "journey", "destination", "exploration", "trip"],
#                     "Fantasy": ["fantasy", "magic", "myth", "legend", "wizard", "dragon", "epic"],
#                     "Mystery/Thriller": ["mystery", "thriller", "detective", "crime", "suspense", "investigation"],
#                     "Romance": ["romance", "love", "passion", "relationship", "heart", "affection"],
#                     "Self-Help": ["self-help", "motivation", "personal development", "growth", "success", "habits"],
#                     "Science Fiction": ["sci-fi", "space", "alien", "future", "technology", "robot"],
#                     "Horror": ["horror", "scary", "ghost", "monster", "haunted", "fear"],
#                     "Children": ["children", "kids", "fairy tale", "adventure", "learning", "nursery"],
#                     "Comedy/Humor": ["comedy", "humor", "funny", "joke", "satire", "parody"],
#                     "Religion/Spirituality": ["religion", "spirituality", "faith", "belief", "prayer", "philosophy"],
#                     "Politics": ["politics", "government", "policy", "diplomacy", "elections", "law"],
#                     "Cooking/Food": ["cooking", "food", "recipe", "culinary", "kitchen", "diet", "nutrition"],
#                     "Travel Guides": ["travel", "destination", "guide", "itinerary", "vacation", "tour"],
#                 }

#                 genre = "Unknown"
#                 for key, keywords in genre_keywords.items():
#                     if any(keyword in text.lower() for keyword in keywords):
#                         genre = key
#                         break
#                 document.genre = genre

#                 # Generate audio using Text-to-Speech
#                 max_length = 3000  # Increased chunk size for fewer chunks
#                 text_chunks = [text[i : i + max_length] for i in range(0, len(text), max_length)]
#                 audio_segments = []

#                 logger.info(f"Processing {len(text_chunks)} text chunks for TTS.")

#                 # Optimize the number of workers based on chunks
#                 max_workers = min(12, len(text_chunks)) if len(text_chunks) > 0 else 1

#                 with ThreadPoolExecutor(max_workers=max_workers) as executor:
#                     audio_chunks = list(
#                         executor.map(
#                             lambda chunk: tts_service.convert_text_to_speech(chunk, detected_language),
#                             text_chunks,
#                         )
#                     )

#                 logger.info("Completed TTS conversion for all chunks.")

#                 for chunk_audio in audio_chunks:
#                     audio_segment = AudioSegment.from_file(io.BytesIO(chunk_audio), format="mp3")
#                     audio_segments.append(audio_segment)

#                 # Combine all audio segments
#                 combined_audio = sum(audio_segments)

#                 # Apply immersive audio effects
#                 immersive_audio = apply_immersive_effects(combined_audio)

#                 # Calculate audio duration in hours and minutes
#                 duration_in_seconds = len(immersive_audio) / 1000  # pydub works in milliseconds
#                 duration_in_minutes = duration_in_seconds // 60
#                 duration_in_hours = duration_in_minutes // 60
#                 formatted_duration = f"{int(duration_in_hours)} hours {int(duration_in_minutes % 60)} minutes"

#                 # Export processed audio to BytesIO
#                 audio_bytes_io = io.BytesIO()
#                 immersive_audio.export(audio_bytes_io, format="mp3", bitrate="128k")
#                 audio_bytes_io.seek(0)

#                 # Upload processed audio to S3
#                 processed_audio_key = f"{settings.S3_FOLDER_NAME}/audio/{user.id}/{document.id}_processed.mp3"
#                 audio_url = s3_handler.upload_file(
#                     file_obj=audio_bytes_io,
#                     bucket=settings.S3_BUCKET_NAME,
#                     key=processed_audio_key,
#                     content_type="audio/mpeg",
#                 )
#                 document.audio_url = audio_url

#                 # Create audiobook record
#                 audiobook_data = AudioBookCreate(
#                     title=document.title,
#                     narrator="Generated Narrator",
#                     duration=formatted_duration,
#                     genre=genre,
#                     publication_date=datetime.utcnow(),
#                     author=document.author,
#                     file_key=processed_audio_key,
#                     url=audio_url,
#                     is_dolby_atmos_supported=True,
#                     document_id=document.id,
#                 )
#                 audiobook = create_audiobook(db=db, audiobook=audiobook_data)

#                 # Link the audiobook to the document
#                 document.audiobook = audiobook
#                 document.processing_status = "completed"
#                 db.commit()

#                 # Record the end time and calculate total processing time
#                 end_time = time.time()
#                 total_processing_time = end_time - start_time
#                 logger.info(f"Total processing time for document {document.id}: {total_processing_time:.2f} seconds")

#                 # Ensure processing time is under 60 seconds
#                 if total_processing_time > 60:
#                     logger.warning(f"Processing time exceeded 60 seconds for document {document.id}: {total_processing_time:.2f} seconds")

#                 # Append the processed document to the list
#                 documents.append(document)

#             except Exception as processing_error:
#                 logger.error(f"Error processing document {document.id}: {str(processing_error)}")
#                 document.processing_status = "failed"
#                 document.processing_error = str(processing_error)
#                 db.commit()
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Document processing failed: {str(processing_error)}",
#                 )

#         except HTTPException as http_exc:
#             logger.error(f"HTTP error uploading document {file.filename}: {str(http_exc.detail)}")
#             db.rollback()
#             raise http_exc
#         except Exception as e:
#             logger.error(f"Error uploading document {file.filename}: {str(e)}")
#             db.rollback()
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Failed to upload document {file.filename}",
#             )

#     return documents


# # List Documents Endpoint

# @router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
# async def list_documents(
#     skip: int = 0,
#     limit: int = 10,
#     search: Optional[str] = None,
#     status: Optional[str] = None,
#     file_type: Optional[str] = None,
#     start_date: Optional[datetime] = None,
#     end_date: Optional[datetime] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Retrieve a list of documents belonging to the current user.
#     """
#     try:
#         filter_params = DocumentFilter(
#             search=search,
#             status=status,
#             file_type=file_type,
#             start_date=start_date,
#             end_date=end_date
#         )
#         documents = get_documents(
#             db=db,
#             user_id=user.id,
#             filter_params=filter_params,
#             skip=skip,
#             limit=limit
#         )
#         return documents
#     except Exception as e:
#         logger.error(f"Error listing documents: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve documents",
#         )


# # Get Document Status Endpoint

# @router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
# def get_document_status(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Retrieve the processing status of a single document.

#     This endpoint returns the document details, including the current
#     `processing_status` (e.g., "pending", "completed", "failed") and the
#     `audio_url` when available.
#     - To learn more about the API, check the [documentation page](https://your-documentation-link)
#     """
#     try:
#         # Query the database for the specified document
#         document = db.query(Document).options(joinedload(Document.audiobook)).filter(
#             Document.id == document_id,
#             Document.user_id == user.id
#         ).first()

#         # Raise an error if the document is not found
#         if not document:
#             raise HTTPException(status_code=404, detail="Document not found")

#         # Return the document details
#         return document

#     except Exception as e:
#         logger.error(f"Error retrieving document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document",
#         )


# # Update Document Endpoint

# @router.put("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
# async def update_document_endpoint(
#     document_id: int,
#     document_update: DocumentUpdate,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Update an existing document's metadata.
#     """
#     try:
#         document = update_document(
#             db=db,
#             document_id=document_id,
#             user_id=user.id,
#             update_data=document_update,
#         )
#         return document
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error updating document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update document",
#         )


# # Delete Document Endpoint

# @router.delete("/{document_id}", status_code=status.HTTP_200_OK)
# async def delete_document_endpoint(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Delete a document by its ID.
#     """
#     try:
#         success = delete_document(db=db, document_id=document_id, user_id=user.id)
#         if success:
#             return {"detail": "Document deleted successfully"}
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Document not found",
#             )
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error deleting document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to delete document",
#         )


# # Get Document Statistics Endpoint

# @router.get("/stats", response_model=DocumentStats)
# async def get_document_stats(
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Get statistics about the documents of the current user.
#     """
#     try:
#         total_docs = db.query(Document).filter(Document.user_id == user.id).count()
#         processed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "completed")
#             .count()
#         )
#         failed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "failed")
#             .count()
#         )
#         total_storage = (
#             db.query(func.sum(Document.file_size))
#             .filter(Document.user_id == user.id)
#             .scalar()
#             or 0
#         )

#         return DocumentStats(
#             total_documents=total_docs,
#             processed_documents=processed_docs,
#             failed_documents=failed_docs,
#             total_storage_used=total_storage / (1024 * 1024),  # Convert bytes to MB
#         )
#     except Exception as e:
#         logger.error(f"Error getting document stats: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document statistics",
#         )



# # app/api/endpoints/user/documents.py

# from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, BackgroundTasks, Query,Request
# from sqlalchemy.orm import Session, joinedload
# import io
# import time
# import logging
# from datetime import datetime
# from app.schemas.document import (
#     DocumentCreate,
#     DocumentFilter,
#     DocumentUpdate,
#     DocumentResponse,
#     DocumentStats,
# )
# from typing import List, Optional
# from app.core.config import settings
# from app.database import get_db
# from app.core.security import get_current_user
# from app.models import User,Document
# from app.schemas import DocumentResponse, DocumentCreate
# from app.services.document_service import process_document, create_document, get_documents, delete_document,update_document 
# from app.services.search_service import   search_documents_with_cache  # Adjust the import path accordingly
# from app.utils.redis_utils import delete_pattern
# from app.utils.s3_utils import s3_handler
# from sqlalchemy import func
# # from app.utils.lang_utils  import map_language_code_to_supported, infer_genre

# logger = logging.getLogger(__name__)


# router = APIRouter(
#     prefix="/documents",
#     tags=["Documents"],  # Ensures the endpoint appears under "Documents" in Swagger
# )

# @router.get("/search", response_model=List[DocumentResponse], summary="Search Documents", description="Unified search endpoint for documents.")
# async def search_documents(
#     request: Request,
#     query: str = Query(..., min_length=1, max_length=100, description="Search query for document titles and descriptions."),
#     page: int = Query(1, ge=1, description="Page number for pagination."),
#     page_size: int = Query(10, ge=1, le=100, description="Number of results per page."),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Search documents for the logged-in user.

#     - **query**: The search keyword to look for in document titles and descriptions.
#     - **Authentication**: User must be authenticated to search their own documents.

#     **Example Request:**
#     ```http
#     GET /documents/search?query=advise HTTP/1.1
#     Host: localhost:8000
#     Authorization: Bearer YOUR_JWT_TOKEN
#     Accept: application/json
#     ```

#     **Example Response:**
#     ```json
#     [
#         {
#             "id": 295,
#             "title": "Annual Report",
#             "author": "JohnDoe",
#             "file_type": "application/pdf",
#             "file_key": "documents/1/20241220115803_annual_report.pdf",
#             "detected_language": "en",
#             "description": "Detailed annual financial report.",
#             "genre": "Finance",
#             "tags": ["Annual", "Finance"],
#             "processing_status": "completed",
#             "processing_error": null,
#             "created_at": "2024-12-20T11:58:05.388672Z"
#         },
#         // ... more documents ...
#     ]
#     ```
#      **Notes:**
#     - Ensure that the `query` parameter is URL-encoded if it contains spaces or special characters.
#     - The search is case-insensitive and matches partial strings within the `title` and `description` fields.
#     - Pagination parameters (`page` and `page_size`) help manage large datasets efficiently.
#     - The endpoint utilizes Redis caching to improve performance on repeated searches.
#     """
#     # Log the request details
#     logger.info(f"Incoming request: {request.method} {request.url}")
#     logger.info(f"Query parameter: {query}")
#     logger.info(f"Current user ID: {current_user.id}")

#     try:
#         # Calculate offset based on page and page_size
#         offset = (page - 1) * page_size
#         # Define additional parameters if needed
#         prefix = query  # Adjust based on your search requirements
#         bucketname = settings.S3_BUCKET_NAME  # Assuming bucket name is stored in settings
#         limits = page_size  # Number of results to limit
#         levels = 1  # Depth levels, adjust as necessary
#         offsets = offset  # Pagination offset

#         owner_id = current_user.id

#         # Use the helper function to perform the search with caching
#         results = search_documents_with_cache(
#             db=db,
#             prefix=prefix,
#             bucketname=bucketname,
#             limits=limits,
#             levels=levels,
#             offsets=offsets,
#             owner_id=owner_id
#         )

#         serialized_results = [DocumentResponse.from_orm(doc) for doc in results]

#         logger.info(f"User {current_user.id} searched for '{query}' and found {len(results)} documents.")
#         return serialized_results

#     except Exception as e:
#         logger.error(f"Error in search_documents: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


# @router.post("/upload/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, summary="Upload a Single Document")
# def upload_document(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Upload a single document, enqueue processing, and return document details.
#     Document maybe .docx or pdf or txt or jpg or png

#     - **file**: The document file to upload. Supported types: PDF, PNG, JPEG, TXT.
#     - **is_public**: Boolean indicating if the document is publicly accessible.
#     - **Authentication**: User must be authenticated to upload documents.

#     **Example Request:**
#     ```bash
#     curl -X POST "http://localhost:8000/documents/upload/" \
#          -H "Authorization: Bearer YOUR_JWT_TOKEN" \
#          -F "file=@/path/to/your/document.pdf" \
#          -F "is_public=true"
#     ```

#     **Example Response:**
#     ```json
#     {
#         "id": 295,
#         "title": "document.pdf",
#         "author": "JohnDoe",
#         "file_type": "application/pdf",
#         "file_key": "documents/1/20241219161550_document.pdf",
#         "detected_language": "en",
#         "description": "Uploaded document.pdf",
#         "genre": "Education",
#         "tags": ["schoolbook", "varlet", "bill of fare", "papers", "id cards", "recommendation"],
#         "processing_status": "processing",
#         "processing_error": null,
#         "created_at": "2024-12-19T16:15:50.888Z"
#     }
#     ```
#     """
#     try:
#         start_time = time.time()

#         # Read the uploaded file content
#         file_content = file.file.read()

#         # Allowed content types
#         ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
#         #ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain"]

#         # Check file type
#         if file.content_type not in ALLOWED_CONTENT_TYPES:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Unsupported file type for processing.",
#             )

#         # Generate the file key for S3 with timestamp to ensure uniqueness
#         timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
#         file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{timestamp}_{file.filename}"

#         # Upload the file to S3
#         s3_url = s3_handler.upload_file(
#             file_obj=io.BytesIO(file_content),
#             bucket=settings.S3_BUCKET_NAME,
#             key=file_key,
#             content_type=file.content_type,
#         )
#         if not s3_url:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload file to S3",
#             )

#         # Create a database record for the document
#         document_data = DocumentCreate(
#             title=file.filename,
#             author=user.username,
#             file_type=file.content_type,
#             file_key=file_key,
#             url=s3_url,
#             is_public=is_public,
#             created_at=datetime.utcnow()
#         )
#         document = create_document(
#             db=db,
#             document_data=document_data,
#             user_id=user.id,
#             file_key=file_key,
#             file_size=len(file_content),
#         )

#         # # Update processing status to "processing"
#         # document.processing_status = "processing"
#         # db.commit()

#         # Enqueue the background task to process the document
#         background_tasks.add_task(
#             process_document,
#             document_id=document.id,
#             user_id=user.id,
#             bucket_name=settings.S3_BUCKET_NAME,
#             file_key=file_key
#         )

     

#         logger.info(f"User {user.id} uploaded document {document.id} and processing started.")

#         return document
        

#     except HTTPException as http_exc:
#         logger.error(f"HTTP error uploading document: {http_exc.detail}")
#         raise http_exc
#     except Exception as e:
#         logger.error(f"Error uploading document: {str(e)}")
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to upload document.",
#         )


# @router.post("/multi-upload/", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED, summary="Upload Multiple Documents")
# def upload_multiple_documents(
#     background_tasks: BackgroundTasks,
#     files: List[UploadFile] = File(...),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Upload multiple documents, enqueue processing for each, and return their details.

#     - **files**: A list of document files to upload. Supported types: PDF, PNG, JPEG, TXT.
#     - **is_public**: Boolean indicating if the documents are publicly accessible.
#     - **Authentication**: User must be authenticated to upload documents.

#     **Example Request:**
#     ```bash
#     curl -X POST "http://localhost:8000/documents/multi-upload/" \
#          -H "Authorization: Bearer YOUR_JWT_TOKEN" \
#          -F "files=@/path/to/your/document1.pdf" \
#          -F "files=@/path/to/your/document2.png" \
#          -F "is_public=false"
#     ```

#     **Example Response:**
#     ```json
#     [
#         {
#             "id": 296,
#             "title": "document1.pdf",
#             "author": "JohnDoe",
#             "file_type": "application/pdf",
#             "file_key": "documents/1/20241219161600_document1.pdf",
#             "detected_language": "en",
#             "description": "Uploaded document1.pdf",
#             "genre": "Education",
#             "tags": ["ledger", "issue", "novel", "letter box"],
#             "processing_status": "processing",
#             "processing_error": null,
#             "created_at": "2024-12-19T16:16:00.123Z"
#         },
#         {
#             "id": 297,
#             "title": "document2.png",
#             "author": "JohnDoe",
#             "file_type": "image/png",
#             "file_key": "documents/1/20241219161600_document2.png",
#             "detected_language": null,
#             "description": "Uploaded document2.png",
#             "genre": "Art",
#             "tags": ["holy writ", "issue", "novel", "postbox"],
#             "processing_status": "processing",
#             "processing_error": null,
#             "created_at": "2024-12-19T16:16:00.123Z"
#         }
#     ]
#     ```
#     """
#     try:
#         documents = []
#         for file in files:
#             # Read the uploaded file content
#             file_content = file.file.read()

#             # Allowed content types
#             ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
#             #ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain"]

#             # Check file type
#             if file.content_type not in ALLOWED_CONTENT_TYPES:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Unsupported file type for {file.filename}.",
#                 )

#             # Generate the file key for S3 with timestamp to ensure uniqueness
#             timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
#             file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{timestamp}_{file.filename}"

#             # Upload the file to S3
#             s3_url = s3_handler.upload_file(
#                 file_obj=io.BytesIO(file_content),
#                 bucket=settings.S3_BUCKET_NAME,
#                 key=file_key,
#                 content_type=file.content_type,
#             )
#             if not s3_url:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Failed to upload {file.filename} to S3.",
#                 )

#             # Create a database record for the document
#             document_data = DocumentCreate(
#                 title=file.filename,
#                 author=user.username,
#                 file_type=file.content_type,
#                 file_key=file_key,
#                 url=s3_url,
#                 is_public=is_public,
#                 created_at=datetime.utcnow()
#             )
#             document = create_document(
#                 db=db,
#                 document_data=document_data,
#                 user_id=user.id,
#                 file_key=file_key,
#                 file_size=len(file_content),
#             )

#             # Update processing status to "processing"
#             document.processing_status = "processing"
#             db.commit()

#             # Enqueue the background task to process the document
#             background_tasks.add_task(
#                 process_document,
#                 document_id=document.id,
#                 user_id=user.id,
#                 bucket_name=settings.S3_BUCKET_NAME,
#                 file_key=file_key
#             )

#             logger.info(f"User {user.id} uploaded document {document.id} and processing started.")

#             documents.append(document)

#         return documents

#     except HTTPException as http_exc:
#         logger.error(f"HTTP error uploading multiple documents: {http_exc.detail}")
#         raise http_exc
#     except Exception as e:
#         logger.error(f"Error uploading multiple documents: {str(e)}")
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to upload documents.",
#         )





# @router.put("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK, summary="Update a Document")
# async def update_document_endpoint(
#     document_id: int,
#     document_update: DocumentUpdate,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Update an existing document's metadata.

#     - **document_id**: ID of the document to update.
#     - **document_update**: Metadata fields to update (e.g., title, description, tags).
#     - **Authentication**: User must be authenticated to update their own documents.

#     **Example Request:**
#     ```http
#     PUT /documents/295 HTTP/1.1
#     Host: localhost:8000
#     Authorization: Bearer YOUR_JWT_TOKEN
#     Content-Type: application/json

#     {
#         "title": "Updated Report",
#         "description": "Updated description of the annual report.",
#         "tags": ["Updated", "Finance"]
#     }
#     ```

#     **Example Response:**
#     ```json
#     {
#         "id": 295,
#         "title": "Updated Report",
#         "author": "JohnDoe",
#         "file_type": "application/pdf",
#         "file_key": "documents/1/20241219161700_updated_report.pdf",
#         "detected_language": "en",
#         "description": "Updated description of the annual report.",
#         "genre": "Finance",
#         "tags": ["Updated", "Finance"],
#         "processing_status": "completed",
#         "processing_error": null,
#         "created_at": "2024-12-19T16:17:00.888Z"
#     }
#     ```
#     """
#     try:
#         document = update_document(
#             db=db,
#             document_id=document_id,
#             user_id=user.id,
#             update_data=document_update,
#         )
#         logger.info(f"User {user.id} updated document {document_id} successfully.")
#         return document
#     except HTTPException as e:
#         logger.error(f"HTTP error updating document {document_id}: {e.detail}")
#         raise e
#     except Exception as e:
#         logger.error(f"Error updating document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update document.",
#         )


# @router.delete("/{document_id}", status_code=status.HTTP_200_OK, summary="Delete a Document")
# async def delete_document_endpoint(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Delete a document by its ID.

#     - **document_id**: ID of the document to delete.
#     - **Authentication**: User must be authenticated to delete their own documents.

#     **Example Request:**
#     ```http
#     DELETE /documents/295 HTTP/1.1
#     Host: localhost:8000
#     Authorization: Bearer YOUR_JWT_TOKEN
#     ```

#     **Example Response:**
#     ```json
#     {
#         "detail": "Document deleted successfully."
#     }
#     ```
#     """
#     try:
#         success = delete_document(db=db, document_id=document_id, user_id=user.id)
#         if success:
#             logger.info(f"User {user.id} deleted document {document_id} successfully.")
#             return {"detail": "Document deleted successfully."}
#         else:
#             logger.warning(f"User {user.id} attempted to delete non-existent document {document_id}.")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Document not found.",
#             )
#     except HTTPException as e:
#         logger.error(f"HTTP error deleting document {document_id}: {e.detail}")
#         raise e
#     except Exception as e:
#         logger.error(f"Error deleting document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to delete document.",
#         )


# @router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK, summary="Get Document Details")
# def get_document_status(
#     document_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Retrieve the processing status and details of a single document.

#     - **document_id**: ID of the document to retrieve.
#     - **Authentication**: User must be authenticated to access their own documents.

#     **Example Request:**
#     ```http
#     GET /documents/295 HTTP/1.1
#     Host: localhost:8000
#     Authorization: Bearer YOUR_JWT_TOKEN
#     Accept: application/json
#     ```

#     **Example Response:**
#     ```json
#     {
#         "id": 295,
#         "title": "Annual Report",
#         "author": "JohnDoe",
#         "file_type": "application/pdf",
#         "file_key": "documents/1/20241219161700_annual_report.pdf",
#         "detected_language": "en",
#         "description": "Detailed annual financial report.",
#         "genre": "Finance",
#         "tags": ["Annual", "Finance"],
#         "processing_status": "completed",
#         "processing_error": null,
#         "created_at": "2024-12-19T16:17:00.888Z"
#     }
#     ```
#     """
#     try:
#         # Query the database for the specified document
#         document = db.query(Document).options(joinedload(Document.audiobook)).filter(
#             Document.id == document_id,
#             Document.user_id == user.id
#         ).first()

#         # Raise an error if the document is not found
#         if not document:
#             logger.warning(f"User {user.id} attempted to access non-existent document {document_id}.")
#             raise HTTPException(status_code=404, detail="Document not found.")

#         logger.info(f"User {user.id} retrieved document {document_id} successfully.")
#         return document

#     except HTTPException as e:
#         logger.error(f"HTTP error retrieving document {document_id}: {e.detail}")
#         raise e
#     except Exception as e:
#         logger.error(f"Error retrieving document {document_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document.",
#         )


# @router.get("/stats", response_model=DocumentStats, status_code=status.HTTP_200_OK, summary="Get Document Statistics")
# async def get_document_stats(
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Get statistics about the documents of the current user.

#     - **total_documents**: Total number of documents uploaded by the user.
#     - **processed_documents**: Number of documents that have been successfully processed.
#     - **failed_documents**: Number of documents that failed processing.
#     - **total_storage_used**: Total storage used by the user's documents in MB.
#     - **Authentication**: User must be authenticated to access statistics.

#     **Example Request:**
#     ```http
#     GET /documents/stats HTTP/1.1
#     Host: localhost:8000
#     Authorization: Bearer YOUR_JWT_TOKEN
#     Accept: application/json
#     ```

#     **Example Response:**
#     ```json
#     {
#         "total_documents": 50,
#         "processed_documents": 45,
#         "failed_documents": 5,
#         "total_storage_used": 120.5
#     }
#     ```
#     """
#     try:
#         total_docs = db.query(Document).filter(Document.user_id == user.id).count()
#         processed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "completed")
#             .count()
#         )
#         failed_docs = (
#             db.query(Document)
#             .filter(Document.user_id == user.id, Document.processing_status == "failed")
#             .count()
#         )
#         total_storage = (
#             db.query(func.sum(Document.file_size))
#             .filter(Document.user_id == user.id)
#             .scalar()
#             or 0
#         )

#         stats = DocumentStats(
#             total_documents=total_docs,
#             processed_documents=processed_docs,
#             failed_documents=failed_docs,
#             total_storage_used=total_storage / (1024 * 1024),  # Convert bytes to MB
#         )
#         logger.info(f"User {user.id} retrieved document statistics successfully.")
#         return stats
#     except Exception as e:
#         logger.error(f"Error getting document stats for user {user.id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve document statistics.",
#         )








# # app/api/endpoints/user/documents.py

# from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
# from sqlalchemy.orm import Session
# import logging
# import io
# from datetime import datetime
# from typing import List

# from app.core.config import settings
# from app.database import get_db
# from app.core.security import get_current_user
# from app.models.user import User
# from app.models.user import SubscriptionType
# from app.schemas.document import DocumentCreate, DocumentResponse
# from app.services.document_service import create_and_process_document
# from app.utils.s3_utils import s3_handler

# logger = logging.getLogger(__name__)

# router = APIRouter(
#     prefix="/documents",
#     tags=["Documents"]
# )

# @router.post("/upload/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
# def upload_document(
#     file: UploadFile = File(...),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     **Synchronous** upload & process a single document:
#     - No background tasks.
#     - Returns fully processed Document with `audiobook` in the response.
#     - Supports PDF, DOCX, PNG, JPEG, and TXT.
#     """
#     try:
#         file_bytes = file.file.read()
#         ALLOWED_CONTENT_TYPES = [
#             "application/pdf",
#             "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#             "image/png",
#             "image/jpeg",
#             "text/plain",
#         ]

#         if file.content_type not in ALLOWED_CONTENT_TYPES:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Unsupported file type. Allowed: PDF, DOCX, PNG, JPEG, TXT",
#             )

#         # Generate S3 key
#         timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
#         file_key = f"{settings.S3_FOLDER_NAME}/{current_user.id}/{timestamp}_{file.filename}"

#         # Upload raw file to S3
#         s3_url = s3_handler.upload_file(
#             file_obj=io.BytesIO(file_bytes),
#             bucket=settings.S3_BUCKET_NAME,
#             key=file_key,
#             content_type=file.content_type
#         )
#         if not s3_url:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload file to S3."
#             )

#         # Prepare DocumentCreate schema
#         doc_data = DocumentCreate(
#             title=file.filename,
#             author=current_user.username,
#             file_type=file.content_type,
#             file_key=file_key,
#             url=s3_url,
#             is_public=is_public,
#             created_at=datetime.utcnow()
#         )

#         # Determine subscription -> "free" or "premium"
#         sub_type_str = "premium" if current_user.subscription_type == SubscriptionType.premium else "free"

#         # Synchronously create & process
#         document = create_and_process_document(
#             db=db,
#             document_data=doc_data,
#             user=current_user,
#             file_content=file_bytes,
#             subscription_type=sub_type_str
#         )

#         # Return the final processed Document (with audiobook)
#         return document

#     except HTTPException as http_ex:
#         logger.error(f"HTTP error during upload_document: {http_ex.detail}")
#         raise http_ex
#     except Exception as ex:
#         logger.error(f"Unhandled error during upload_document: {str(ex)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to process the document."
#         )





# app/api/endpoints/user/documents.py

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends
)
from sqlalchemy.orm import Session
import logging
import io
from datetime import datetime
from typing import List, Optional
import time
from app.core.config import settings
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User, SubscriptionType
from app.models import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentFilter, DocumentResponse
from app.services.document_service import (
    create_and_process_document,
    get_documents,
    update_document as update_document_service,
    delete_document as delete_document_service
)
from app.utils.s3_utils import s3_handler

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# ------------------------------------------------------------------------------
# 1) Single File Upload (Synchronous)
# ------------------------------------------------------------------------------
@router.post("/upload/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    is_public: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Synchronous** upload & process a single document:
    - No background tasks.
    - Returns fully processed Document with `audiobook` in the response.
    - Supports PDF, DOCX, PNG, JPEG, and TXT.
    """
    try:
        
        # Start endpoint processing time
        endpoint_start_time = time.time()
        file_bytes = file.file.read()
        ALLOWED_CONTENT_TYPES = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/png",
            "image/jpeg",
            "text/plain",
        ]

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Allowed: PDF, DOCX, PNG, JPEG, TXT",
            )

        # Generate S3 key
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        file_key = f"{settings.S3_FOLDER_NAME}/{current_user.id}/{timestamp}_{file.filename}"

        # Upload raw file to S3
        s3_url = s3_handler.upload_file(
            file_obj=io.BytesIO(file_bytes),
            bucket=settings.S3_BUCKET_NAME,
            key=file_key,
            content_type=file.content_type
        )
        if not s3_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to S3."
            )

        # Prepare DocumentCreate schema
        doc_data = DocumentCreate(
            title=file.filename,
            author=current_user.username,
            file_type=file.content_type,
            file_key=file_key,
            url=s3_url,
            is_public=is_public,
            created_at=datetime.utcnow()
        )

        # Determine subscription -> "free" or "premium"
        sub_type_str = "premium" if current_user.subscription_type == SubscriptionType.premium else "free"

        # Synchronously create & process
        document = create_and_process_document(
            db=db,
            document_data=doc_data,
            user=current_user,
            file_content=file_bytes,
            subscription_type=sub_type_str
        )

        # End endpoint processing time
        endpoint_end_time = time.time()
        total_endpoint_time = endpoint_end_time - endpoint_start_time
        logger.info(f"[ENDPOINT] Total time for /upload/ request: {total_endpoint_time:.2f} seconds.")


        # Return the final processed Document (with audiobook)
        return document

    except HTTPException as http_ex:
        logger.error(f"HTTP error during upload_document: {http_ex.detail}")
        raise http_ex
    except Exception as ex:
        logger.error(f"Unhandled error during upload_document: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process the document."
        )


# ------------------------------------------------------------------------------
# 2) Multiple Files Upload (Synchronous for each file)
# ------------------------------------------------------------------------------
@router.post("/multi-upload/", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    is_public: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Synchronous** upload & process multiple documents in one request:
    - Loops over each file and processes it (OCR + TTS) immediately.
    - Returns a list of fully processed Document objects (with `audiobook`).
    - Supports PDF, DOCX, PNG, JPEG, and TXT.
    """
    try:
        # Start endpoint processing time
        endpoint_start_time = time.time()
        ALLOWED_CONTENT_TYPES = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/png",
            "image/jpeg",
            "text/plain",
        ]
        sub_type_str = "premium" if current_user.subscription_type == SubscriptionType.premium else "free"

        documents = []
        for file in files:
            file_bytes = file.file.read()
            if file.content_type not in ALLOWED_CONTENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file.filename}",
                )

            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            file_key = f"{settings.S3_FOLDER_NAME}/{current_user.id}/{timestamp}_{file.filename}"

            s3_url = s3_handler.upload_file(
                file_obj=io.BytesIO(file_bytes),
                bucket=settings.S3_BUCKET_NAME,
                key=file_key,
                content_type=file.content_type
            )
            if not s3_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload {file.filename} to S3."
                )

            doc_data = DocumentCreate(
                title=file.filename,
                author=current_user.username,
                file_type=file.content_type,
                file_key=file_key,
                url=s3_url,
                is_public=is_public,
                created_at=datetime.utcnow()
            )

            document = create_and_process_document(
                db=db,
                document_data=doc_data,
                user=current_user,
                file_content=file_bytes,
                subscription_type=sub_type_str
            )
            file_end_time = time.time()
            file_processing_time = file_end_time - file_start_time
            logger.info(f"[ENDPOINT] Document {document.id} processed in {file_processing_time:.2f} seconds.")

            documents.append(document)
        # End endpoint processing time
        endpoint_end_time = time.time()
        total_endpoint_time = endpoint_end_time - endpoint_start_time
        logger.info(f"[ENDPOINT] Total time for /multi-upload/ request: {total_endpoint_time:.2f} seconds.")
        return documents

    except HTTPException as http_ex:
        logger.error(f"HTTP error during upload_multiple_documents: {http_ex.detail}")
        raise http_ex
    except Exception as ex:
        logger.error(f"Unhandled error during upload_multiple_documents: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process documents."
        )


# ------------------------------------------------------------------------------
# 3) Retrieve Documents (List or Single)
# ------------------------------------------------------------------------------
@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
def list_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    """
    Retrieve a list of your documents with optional search, skip, and limit.
    """
    filter_params = DocumentFilter(search=search)
    results = get_documents(db, user_id=current_user.id, filter_params=filter_params, skip=skip, limit=limit)
    return results


@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
def get_document_by_id(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a single Document by its ID.
    """
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return document


# ------------------------------------------------------------------------------
# 4) Update Document Metadata (No Reprocessing by Default)
# ------------------------------------------------------------------------------
@router.put("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
def update_document(
    document_id: int,
    doc_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing document's metadata (title, description, tags, etc.).
    No re-OCR/TTS by default.
    """
    try:
        document = update_document_service(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
            document_update=doc_update
        )
        return document
    except HTTPException as http_ex:
        logger.error(f"HTTP error updating document {document_id}: {http_ex.detail}")
        raise http_ex
    except Exception as ex:
        logger.error(f"Unhandled error updating document {document_id}: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document."
        )


# ------------------------------------------------------------------------------
# 5) Delete Document
# ------------------------------------------------------------------------------
@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document by its ID.
    """
    try:
        success = delete_document_service(db=db, document_id=document_id, user_id=current_user.id)
        if success:
            return {"detail": "Document deleted successfully."}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    except HTTPException as http_ex:
        logger.error(f"HTTP error deleting document {document_id}: {http_ex.detail}")
        raise http_ex
    except Exception as ex:
        logger.error(f"Unhandled error deleting document {document_id}: {str(ex)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document."
        )
