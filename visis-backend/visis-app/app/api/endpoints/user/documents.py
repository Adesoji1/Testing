
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import io

from pydantic import BaseModel
from app.models import Document, User
from app.schemas.document import (
    DocumentCreate,
    DocumentFilter,
    DocumentUpdate,
    DocumentResponse,
    DocumentStats,
)
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
from app.utils.s3_utils import s3_handler
from app.services.tts_service import TTSService
from app.services.ocr_service import ocr_service
from sqlalchemy import func

# Initialize TTS Service
tts_service = TTSService(region_name=settings.REGION_NAME)

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

# # Upload Document Endpoint first correct method
# @router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
# async def upload_document(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     is_public: bool = False,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user),
# ):
#     try:
#         file_content = await file.read()

#         if len(file_content) > settings.MAX_UPLOAD_SIZE:
#             raise HTTPException(
#                 status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                 detail=f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB",
#             )

#         file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

#         # Upload file to S3
#         s3_url = await s3_handler.upload_file(
#             file_obj=io.BytesIO(file_content),
#             bucket=settings.S3_BUCKET_NAME,
#             key=file_key,
#             content_type=file.content_type,
#         )

#         if not s3_url:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to upload file to storage",
#             )

#         # Create document record
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
#             document=document_data,
#             user_id=user.id,
#             file_key=file_key,
#             file_size=len(file_content),
#         )

#         # Start background processing
#         background_tasks.add_task(process_document, document.id)

#         return document

#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error uploading document: {str(e)}")
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to upload document",
#         )


# ###Slow
@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    is_public: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Upload a new document for processing.

    This endpoint uploads a document, processes it for OCR and TTS, and returns
    the document details including the `audio_url` upon completion.
    """
    try:
        # Read the uploaded file content
        file_content = await file.read()

        # Check file size limit
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB",
            )

        # Generate the file key for S3
        file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

        # Upload the file to S3
        s3_url = await s3_handler.upload_file(
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

        # Process the document (OCR and TTS)
        try:
            # Extract text using OCR
            if document.file_type == "application/pdf":
                text, _ = await ocr_service.extract_text_from_pdf(settings.S3_BUCKET_NAME, document.file_key)
            elif document.file_type.startswith("image/"):
                text, _ = await ocr_service.extract_text_from_image(settings.S3_BUCKET_NAME, document.file_key)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file type for processing.",
                )

            # Generate audio using TTS
            max_length = 3000
            text_chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
            audio_bytes_io = io.BytesIO()

            for chunk in text_chunks:
                chunk_audio = await tts_service.convert_text_to_speech(chunk)
                audio_bytes_io.write(chunk_audio)

            audio_bytes_io.seek(0)  # Reset the cursor to the beginning

            # Upload the generated audio file to S3
            audio_key = f"{settings.S3_FOLDER_NAME}/audio/{user.id}/{document.id}.mp3"
            audio_url = await s3_handler.upload_file(
                file_obj=audio_bytes_io,
                bucket=settings.S3_BUCKET_NAME,
                key=audio_key,
                content_type="audio/mpeg",
            )

            # Update the document with the generated audio URL
            document.audio_url = audio_url
            document.audio_key = audio_key
            document.processing_status = "completed"
            db.commit()
            db.refresh(document)

        except Exception as processing_error:
            document.processing_status = "failed"
            document.processing_error = str(processing_error)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {str(processing_error)}",
            )

        # Return the document details, including the audio URL
        return document

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
        document = db.query(Document).filter(
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
