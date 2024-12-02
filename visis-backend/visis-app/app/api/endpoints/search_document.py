from fastapi import APIRouter, Query, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import json
from app.models import Document, User  # Import User model
from app.schemas.document import DocumentResponse
from app.database import get_db
from app.utils.redis_utils import redis_client
from app.core.config import settings
from app.api.endpoints.user.auth import get_current_user
from fastapi.encoders import jsonable_encoder
import logging

router = APIRouter(prefix="/documents", tags=["documents"])

logger = logging.getLogger("search_document")
logger.setLevel(logging.DEBUG)

@router.get(
    "/search",
    response_model=List[DocumentResponse],
    summary="Search Documents",
    description="Unified search endpoint for documents."
)
async def search_documents(
    request: Request,
    query: str = Query(..., min_length=1, max_length=100, description="Search query for document titles"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Ensure correct type hinting
):
    """
    Search documents for the logged-in user.
    """
    # Log the request details
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Query parameter: {query}")
    logger.info(f"Current user ID: {current_user.id}")

    try:
        # Handle search query
        cache_key = f"user:{current_user.id}:search:{query}"
        cached_results = redis_client.get(cache_key)
        if cached_results:
            logger.info(f"Cache hit for key: {cache_key}")
            return json.loads(cached_results)

        results = db.query(Document).filter(
            Document.title.ilike(f"%{query}%"),
            Document.user_id == current_user.id
        ).order_by(Document.upload_date.desc()).all()

        serialized_results = [DocumentResponse.from_orm(doc) for doc in results]

        # Use jsonable_encoder to make data JSON serializable
        json_serializable_data = jsonable_encoder(serialized_results)
        redis_client.setex(cache_key, settings.REDIS_CACHE_TTL, json.dumps(json_serializable_data))

        return serialized_results  # FastAPI will handle the serialization for the response

    except Exception as e:
        logger.error(f"Error in search_documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

