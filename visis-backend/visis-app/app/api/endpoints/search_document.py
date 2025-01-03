# from fastapi import APIRouter, Query, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from typing import List
# import json
# from app.models import Document, User  # Import User model
# from app.schemas.document import DocumentResponse
# from app.database import get_db
# from app.utils.redis_utils import redis_client
# from app.core.config import settings
# from app.api.endpoints.user.auth import get_current_user
# from fastapi.encoders import jsonable_encoder
# import logging


# router = APIRouter(prefix="/documents", tags=["documents"])

# logger = logging.getLogger("search_document")
# logger.setLevel(logging.DEBUG)


# @router.get("/search", response_model=List[DocumentResponse], summary="Search Documents", description="Unified search endpoint for documents.")
# async def search_documents(
#     request: Request,
#     query: str = Query(..., min_length=1, max_length=100, description="Search query for document titles and descriptions."),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Search documents for the logged-in user.

#     - **query**: The search keyword to look for in document titles and descriptions.
#     - **Authentication**: User must be authenticated to search their own documents.

#     **Example Request:**
#     ```http
#     GET /documents/search?query=report HTTP/1.1
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
#             "file_key": "documents/1/20241219161700_annual_report.pdf",
#             "detected_language": "en",
#             "description": "Detailed annual financial report.",
#             "genre": "Finance",
#             "tags": ["Annual", "Finance"],
#             "processing_status": "completed",
#             "processing_error": null,
#             "created_at": "2024-12-19T16:17:00.888Z"
#         },
#         // ... more documents ...
#     ]
#     ```
#     """
#     # Log the request details
#     logger.info(f"Incoming request: {request.method} {request.url}")
#     logger.info(f"Query parameter: {query}")
#     logger.info(f"Current user ID: {current_user.id}")

#     try:
#         # Handle search query
#         cache_key = f"user:{current_user.id}:search:{query}"
#         cached_results = settings.REDIS_CLIENT.get(cache_key)
#         if cached_results:
#             logger.info(f"Cache hit for key: {cache_key}")
#             return json.loads(cached_results)

#         # Perform the search
#         results = db.query(Document).filter(
#             Document.title.ilike(f"%{query}%"),
#             Document.user_id == current_user.id
#         ).order_by(Document.created_at.desc()).all()

#         serialized_results = [DocumentResponse.from_orm(doc) for doc in results]

#         # Use jsonable_encoder to make data JSON serializable
#         json_serializable_data = jsonable_encoder(serialized_results)
#         settings.REDIS_CLIENT.setex(cache_key, settings.REDIS_CACHE_TTL, json.dumps(json_serializable_data))

#         logger.info(f"User {current_user.id} searched for '{query}' and found {len(results)} documents.")
#         return serialized_results  # FastAPI will handle the serialization for the response

#     except Exception as e:
#         logger.error(f"Error in search_documents: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

# app/api/endpoints/search_document.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.document import DocumentResponse, DocumentFilter
from app.services.document_service import get_documents

router = APIRouter()

@router.get("/search", response_model=List[DocumentResponse])
def search_documents(
    query: Optional[str] = Query(None, description="Search term to filter documents by title or description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for documents owned by the current user. Matches partial titles or descriptions.

    - **query**: A search term to filter documents by title or description.
      If omitted, returns all user's documents.

    **Example Request:**
    "GET /search?query=letterofintroduction HTTP/1.1"
    ```bash
    curl -X GET "http://localhost:8000/search?query=report" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN"
    ```

    **Example Response:**
    ```json
    [
      {
        "id": 10,
        "title": "Annual Report",
        "author": "john",
        "file_type": "application/pdf",
        "file_key": "DevIngestion/1/20241220173056_annual_report.pdf",
        "is_public": false,
        "url": "https://presigned-url.pdf",
        "created_at": "2024-12-20T17:30:58.628417",
        "description": "Excerpt of the annual report...",
        "tags": [],
        "detected_language": "English",
        "genre": "Business/Finance",
        "processing_status": "completed",
        "processing_error": null,
        "user_id": 1,
        "upload_date": "2024-12-20T17:30:58.628417",
        "file_size": 102400,
        "audio_url": "https://presigned-url-to-audio",
        "audiobook": {
          "id": 5,
          "title": "Annual Report",
          "narrator": "Generated Narrator",
          "duration": "0 hours 2 minutes",
          "genre": "Business/Finance",
          "publication_date": "2024-12-20T17:30:59.000Z",
          "author": "john",
          "url": "https://presigned-url-to-audio",
          "is_dolby_atmos_supported": false
        }
      }
    ]
    ```
    """
    filter_params = DocumentFilter(search=query)
    documents = get_documents(db, user_id=current_user.id, filter_params=filter_params, skip=0, limit=50)
    return documents
