
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
from sqlalchemy import func

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

# Upload Document Endpoint
@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    is_public: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        file_content = await file.read()

        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB",
            )

        file_key = f"{settings.S3_FOLDER_NAME}/{user.id}/{file.filename}"

        # Upload file to S3
        s3_url = await s3_handler.upload_file(
            file_obj=io.BytesIO(file_content),
            bucket=settings.S3_BUCKET_NAME,
            key=file_key,
            content_type=file.content_type,
        )

        if not s3_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage",
            )

        # Create document record
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

        # Start background processing
        background_tasks.add_task(process_document, document.id)

        return document

    except HTTPException as e:
        raise e
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