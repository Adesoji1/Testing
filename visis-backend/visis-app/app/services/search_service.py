# app/services/search_service.py

from typing import List,Dict
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from app.models import Document
from app.schemas.document import DocumentResponse
from app.core.config import settings  # Assuming settings has REDIS_CLIENT and other configs
from app.utils.redis_utils    import redis_client 

logger = logging.getLogger(__name__)



# def search_documents_with_cache(db: Session, prefix: str, bucketname: str, limits: int, levels: int, offsets: int, user_id: int):
#     """Search documents with Redis caching."""
#     cache_key = f"search:{prefix}:{bucketname}:{limits}:{levels}:{offsets}"
#     cached_result = redis_client.get(cache_key)

#     if cached_result:
#         return json.loads(cached_result)

#     query = """
#     WITH files_folders AS (
#         SELECT ((string_to_array(objects.name, '/'))[%(levels)s]) AS folder
#         FROM storage.objects
#         WHERE objects.name ILIKE %(prefix)s || '%'
#         AND bucket_id = %(bucketname)s
#         AND user_id = %(user_id)s
#         GROUP BY folder
#         LIMIT %(limits)s
#         OFFSET %(offsets)s
#     )
#     SELECT files_folders.folder AS name, objects.id, objects.updated_at,
#            objects.created_at, objects.last_accessed_at, objects.metadata
#     FROM files_folders
#     LEFT JOIN storage.objects
#     ON %(prefix)s || files_folders.folder = objects.name
#        AND objects.bucket_id = %(bucketname)s
#        AND objects.user_id = %(user_id)s;
#     """
#     result = db.execute(query, {
#         "prefix": prefix,
#         "bucketname": bucketname,
#         "user_id": user_id,
#         "limits": limits,
#         "levels": levels,
#         "offsets": offsets,
#     }).fetchall()

#     serialized_result = [
#         {
#             "name": row.name,
#             "id": row.id,
#             "updated_at": row.updated_at,
#             "created_at": row.created_at,
#             "last_accessed_at": row.last_accessed_at,
#             "metadata": row.metadata,
#         }
#         for row in result
#     ]

#     redis_client.set(cache_key, json.dumps(serialized_result), ex=80640)
#     return serialized_result


def search_documents_with_cache(
    db: Session,
    prefix: str,
    bucketname: str,
    limits: int,
    levels: int,
    offsets: int,
    owner_id: int
) -> List[Dict]:
    """
    Search documents with Redis caching.

    Args:
        db (Session): SQLAlchemy session.
        prefix (str): Search prefix/query.
        bucketname (str): S3 bucket name.
        limits (int): Number of results to return.
        levels (int): Depth levels for search (unused here, kept for consistency).
        offsets (int): Pagination offset.
        owner_id (int): ID of the user performing the search.

    Returns:
        List[Dict]: List of documents matching the search criteria.
    """

    cache_key = f"search:{prefix}:{bucketname}:{limits}:{levels}:{offsets}:user:{owner_id}"
    cached_result = redis_client.get(cache_key)

    if cached_result:
        logger.info(f"Cache hit for key: {cache_key}")
        return json.loads(cached_result)

    # Search query: match 'name' or 'metadata->>'description''
    search_pattern = f"%{prefix}%"

    query = text("""
    SELECT 
        id, 
        name, 
        owner, 
        metadata, 
        created_at, 
        updated_at, 
        last_accessed_at, 
        bucket_id, 
        path_tokens, 
        version, 
        user_metadata
    FROM 
        storage.objects
    WHERE 
        (name ILIKE :search_pattern OR metadata->>'description' ILIKE :search_pattern)
        AND bucket_id = :bucketname
        AND owner = :owner_id
    ORDER BY created_at DESC
    LIMIT :limits
    OFFSET :offsets;
    """)

    try:
        result = db.execute(query, {
            "search_pattern": search_pattern,
            "bucketname": bucketname,
            "owner_id": owner_id,
            "limits": limits,
            "offsets": offsets,
        }).fetchall()

        # Convert SQLAlchemy Row objects to dictionaries
        documents = [dict(row) for row in result]

        # Serialize documents to match DocumentResponse schema
        serialized_result = []
        for doc in documents:
            # Extract necessary fields
            serialized_doc = {
                "id": doc["id"],
                "title": doc["name"],
                "author": doc["author"] if "author" in doc else "Unknown",
                "file_type": doc["file_type"] if "file_type" in doc else "application/octet-stream",
                "file_key": doc["file_key"],
                "is_public": doc["metadata"].get("is_public", False) if doc["metadata"] else False,
                "url": f"https://{bucketname}.s3.{settings.AWS_REGION}.amazonaws.com/{doc['file_key']}",
                "created_at": doc["created_at"].isoformat(),
                "description": doc["metadata"].get("description", "") if doc["metadata"] else "",
                "tags": doc["metadata"].get("tags", []) if doc["metadata"] else [],
                "detected_language": doc["metadata"].get("detected_language", "Unknown") if doc["metadata"] else "Unknown",
                "genre": doc["metadata"].get("genre", "Uncategorized") if doc["metadata"] else "Uncategorized",
                "processing_status": doc["metadata"].get("processing_status", "unknown") if doc["metadata"] else "unknown",
                "processing_error": doc["metadata"].get("processing_error", None) if doc["metadata"] else None,
                "user_id": doc["owner"],
                "upload_date": doc["created_at"].isoformat(),
                "file_size": doc["metadata"].get("file_size", 0) if doc["metadata"] else 0,
                "audio_url": doc["metadata"].get("audio_url", "") if doc["metadata"] else "",
                "audiobook": doc["user_metadata"] if doc["user_metadata"] else None,
            }

            serialized_result.append(serialized_doc)

        # Cache the results with a TTL (e.g., 60 seconds)
        redis_client.setex(cache_key, settings.REDIS_CACHE_TTL, json.dumps(serialized_result))
        logger.info(f"Cached search results for key: {cache_key}")

        return serialized_result

    except Exception as e:
        logger.error(f"Error executing search query: {e}", exc_info=True)
        raise e




# def search_documents_with_cache(
#     db: Session,
#     prefix: str,
#     bucketname: str,
#     limits: int,
#     levels: int,
#     offsets: int,
#     owner_id: str  # Changed from user_id: int to owner_id: str
# ) -> List[dict]:
#     """Search documents with Redis caching."""

#     cache_key = f"search:{prefix}:{bucketname}:{limits}:{levels}:{offsets}:user:{owner_id}"
#     cached_result = redis_client.get(cache_key)

#     if cached_result:
#         logger.info(f"Cache hit for key: {cache_key}")
#         return json.loads(cached_result)

#     query = text("""
#     WITH files_folders AS (
#         SELECT ((string_to_array(objects.name, '/'))[:levels]) AS folder
#         FROM storage.objects
#         WHERE objects.name ILIKE :prefix || '%%'
#         AND bucket_id = :bucketname
#         AND owner_id = :owner_id
#         GROUP BY folder
#         LIMIT :limits
#         OFFSET :offsets
#     )
#     SELECT files_folders.folder AS name, objects.id, objects.updated_at,
#            objects.created_at, objects.last_accessed_at, objects.metadata
#     FROM files_folders
#     LEFT JOIN storage.objects
#     ON :prefix || files_folders.folder = objects.name
#        AND objects.bucket_id = :bucketname
#        AND objects.owner_id = :owner_id;
#     """)

#     try:
#         result = db.execute(query, {
#             "prefix": prefix,
#             "bucketname": bucketname,
#             "owner_id": owner_id,
#             "limits": limits,
#             "levels": levels,
#             "offsets": offsets,
#         }).fetchall()

#         # Convert raw SQL results to a list of dictionaries matching DocumentResponse schema
#         serialized_result = []
#         for row in result:
#             # Fetch the Document instance by id to leverage ORM and relationships
#             document = db.query(Document).filter(Document.id == row.id, Document.owner_id == owner_id).first()
#             if document:
#                 serialized_result.append(DocumentResponse.from_orm(document).dict())
#             else:
#                 # Handle cases where the document might not exist
#                 serialized_result.append({
#                     "id": row.id,
#                     "title": row.name,
#                     "author": "Unknown",  # Replace with actual data if available
#                     "file_type": "application/pdf",  # Replace with actual data if available
#                     "file_key": f"{prefix}/{row.name}",
#                     "detected_language": "en",  # Replace with actual detection logic
#                     "description": row.metadata.get('description', '') if row.metadata else "",
#                     "genre": "Unknown",  # Replace with actual data if available
#                     "tags": [],
#                     "processing_status": "completed",  # Replace with actual status if available
#                     "processing_error": None,
#                     "created_at": row.created_at.isoformat() if row.created_at else None,
#                     "user_id": owner_id,  # Updated to owner_id
#                     "upload_date": row.created_at.isoformat() if row.created_at else None,
#                     "file_size": 0,  # Replace with actual file size retrieval logic
#                     "audio_url": "",  # Replace with actual audio URL retrieval logic
#                     "audiobook": None,  # Replace with actual audiobook retrieval logic
#                 })

#         # Cache the results
#         redis_client.setex(cache_key, settings.REDIS_CACHE_TTL, json.dumps(serialized_result))
#         logger.info(f"Cached search results for key: {cache_key}")
#         return serialized_result

#     except Exception as e:
#         logger.error(f"Error executing search query: {e}", exc_info=True)
#         raise e

# def search_documents_with_cache(db: Session, prefix: str, bucketname: str, limits: int, levels: int, offsets: int, user_id: int) -> List[Document]:
#     """Search documents with Redis caching."""
#     cache_key = f"search:{prefix}:{bucketname}:{limits}:{levels}:{offsets}:user:{user_id}"
#     cached_result = redis_client.get(cache_key)

#     if cached_result:
#         return json.loads(cached_result)

#     query = text("""
#     WITH files_folders AS (
#         SELECT ((string_to_array(objects.name, '/'))[:levels]) AS folder
#         FROM storage.objects
#         WHERE objects.name ILIKE :prefix || '%'
#         AND bucket_id = :bucketname
#         AND owner_id = :user_id
#         GROUP BY folder
#         LIMIT :limits
#         OFFSET :offsets
#     )
#     SELECT files_folders.folder AS name, objects.id, objects.updated_at,
#            objects.created_at, objects.last_accessed_at, objects.metadata
#     FROM files_folders
#     LEFT JOIN storage.objects
#     ON :prefix || files_folders.folder = objects.name
#        AND objects.bucket_id = :bucketname
#        AND objects.owner_id = :user_id;
#     """)

#     result = db.execute(query, {
#         "prefix": prefix,
#         "bucketname": bucketname,
#         "user_id": user_id,
#         "limits": limits,
#         "levels": levels,
#         "offsets": offsets,
#     }).fetchall()

#     # Convert raw SQL results to DocumentResponse or appropriate schema
#     serialized_result = [
#         {
#             "id": row.id,
#             "title": row.name,  # Assuming 'name' corresponds to 'title'
#             "author": "Unknown",  # Replace with actual data if available
#             "file_type": "application/pdf",  # Replace with actual data if available
#             "file_key": f"{prefix}/{row.name}",
#             "detected_language": "en",  # Replace with actual detection logic
#             "description": row.metadata.get('description', '') if row.metadata else "",
#             "genre": "Unknown",  # Replace with actual data if available
#             "tags": [],  # Replace with actual tag retrieval logic
#             "processing_status": "completed",  # Replace with actual status if available
#             "processing_error": None,
#             "created_at": row.created_at.isoformat() if row.created_at else None,
#             "user_id": user_id,
#             "upload_date": row.created_at.isoformat() if row.created_at else None,
#             "file_size": 0,  # Replace with actual file size retrieval logic
#             "audio_url": "",  # Replace with actual audio URL retrieval logic
#             "audiobook": None,  # Replace with actual audiobook retrieval logic
#         }
#         for row in result
#     ]

#     redis_client.set(cache_key, json.dumps(serialized_result), ex=80640)  # TTL in seconds
#     return serialized_result

