# # # app/api/endpoints/user/audiobook.py

# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,status
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.user import User, SubscriptionType
# from app.core.security import get_current_user
# from app.core.config import settings
# from app.models.document import Document
# from app.utils.s3_utils import s3_handler
# from datetime import datetime
# import io
# from app.schemas.document import DocumentCreate , DocumentFilter, DocumentResponse
# #     DocumentUpdate,
# #     DocumentResponse,
# #     DocumentStats,

# from app.services.document_service import  create_document
# from typing import List, Optional
# from app.services.document_service import get_documents
# # from app.core.config import settings
# # from app.database import get_db
# # from app.core.security import get_current_user
# # from app.models import User,Document
# # from app.schemas import DocumentResponse, DocumentCreate
# # 




# router = APIRouter()

# @router.post("/audiobook/upload")
# async def upload_pdf_for_audiobook(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Upload a PDF (or image) as a premium user and get an immersive audiobook (Dolby Atmos).

#     **Example Request:**
#     ```bash
#     curl -X POST "http://localhost:8000/user/audiobook/upload" \
#          -H "Authorization: Bearer YOUR_JWT_TOKEN" \
#          -F "file=@/path/to/your/document.pdf"
#     ```

#     **Example Response (Immersive audio):**
#     ```json
#     {
#       "detail": "Audiobook created successfully.",
#       "document": {
#         "title": "Uploaded Document",
#         "author": "Unknown",
#         "file_type": "application/pdf",
#         "file_key": "audiobook/1/1700000000_document.pdf",
#         "is_public": false,
#         "url": "https://presigned-url",
#         "created_at": "2024-12-20T15:53:55.855Z",
#         "description": "Extracted summary",
#         "tags": [],
#         "detected_language": "English",
#         "genre": "Education",
#         "processing_status": "completed",
#         "processing_error": null,
#         "id": 11,
#         "user_id": 1,
#         "upload_date": "2024-12-20T15:53:55.855Z",
#         "file_size": 0,
#         "audio_url": "https://presigned-url-to-immersive-audio",
#         "audiobook": {
#           "id": 6,
#           "title": "Uploaded Document",
#           "narrator": "Generated Narrator",
#           "duration": "0 hours 1 minutes",
#           "genre": "Education",
#           "publication_date": "2024-12-20T15:53:55.855Z",
#           "author": "Unknown",
#           "url": "https://presigned-url-to-immersive-audio",
#           "is_dolby_atmos_supported": true
#         }
#       }
#     }
#     ```
#     """
#     if current_user.subscription_type != SubscriptionType.premium:
#         raise HTTPException(status_code=403, detail="Endpoint reserved for premium users.")

#     ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain","application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
#     if file.content_type not in ALLOWED_CONTENT_TYPES:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")

#     file_content = await file.read()
#     timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
#     file_key = f"{settings.S3_FOLDER_NAME}/{current_user.id}/{timestamp}_{file.filename}"

#     s3_url = s3_handler.upload_file(
#         file_obj=io.BytesIO(file_content),
#         bucket=settings.S3_BUCKET_NAME,
#         key=file_key,
#         content_type=file.content_type
#     )
#     if not s3_url:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to upload file to S3."
#         )

#     document_data = DocumentCreate(
#         title=file.filename,
#         author=current_user.username,
#         file_type=file.content_type,
#         file_key=file_key,
#         url=s3_url,
#         is_public=False,
#         created_at=datetime.utcnow()
#     )

#     # Pass subscription_type = "premium"
#     document = create_document(
#         db=db,
#         document_data=document_data,
#         user_id=current_user.id,
#         file_key=file_key,
#         file_size=len(file_content),
#         subscription_type="premium"
#     )

#     return {"detail": "Audiobook created successfully.", "document": document}


# @router.get(
#     "/audiobook/my_audiobooks",
#     response_model=List[DocumentResponse],
#     status_code=status.HTTP_200_OK,
#     summary="Retrieve My Audiobooks",
#     description="""
#     Retrieve audiobooks for a premium user.

#     **Example Request:**
#     ```bash
#     curl -X GET "http://localhost:8000/user/audiobook/my_audiobooks" \
#          -H "Authorization: Bearer YOUR_JWT_TOKEN"
#     ```

#     **Example Response:**
#     ```json
#     [
#       {
#         "is_public": false,
#         "audio_url": "https://visis-audiobooks-data.s3.amazonaws.com/DevIngestion/audio/26/313_processed.mp3?...",
#         "title": "Business Open Day pitch structure.pdf",
#         "url": "https://visis-audiobooks-data.s3.amazonaws.com/DevIngestion/26/20241224172617_Business%20Open%20Day%20pitch%20structure.pdf?...",
#         "file_key": "DevIngestion/26/20241224172617_Business Open Day pitch structure.pdf",
#         "id": 313,
#         "upload_date": "2024-12-24T17:26:19.302025",
#         "detected_language": "English",
#         "processing_status": "completed",
#         "genre": "Fiction",
#         "processing_error": null,
#         "created_at": "2024-12-24T17:26:19.301812+00:00",
#         "author": "string1",
#         "file_size": 75997,
#         "file_type": "application/pdf",
#         "description": "Structure for 3-mins pitch...",
#         "tags": [],
#         "audiobook": {
#           "id": 6,
#           "title": "Business Open Day pitch structure.pdf",
#           "narrator": "Generated Narrator",
#           "duration": "0 hours 1 minutes",
#           "genre": "Fiction",
#           "publication_date": "2024-12-24T17:26:19.303Z",
#           "author": "string1",
#           "url": "https://visis-audiobooks-data.s3.amazonaws.com/DevIngestion/audio/26/313_processed.mp3?...",
#           "is_dolby_atmos_supported": true
#         }
#       }
#     ]
#     ```
#     """
# )
# def get_my_audiobooks(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Retrieve audiobooks for a premium user.
#     """
#     if current_user.subscription_type != SubscriptionType.premium:
#         raise HTTPException(status_code=403, detail="Endpoint reserved for premium users.")
    
#     # Retrieve documents with Audiobook eagerly loaded
#     documents = get_documents(
#         db=db,
#         user_id=current_user.id,
#         filter_params=DocumentFilter(),
#         skip=0,
#         limit=50
#     )

#     # Filter only those that have an associated Audiobook
#     audiobooks = [doc for doc in documents if doc.audiobook]

#     return audiobooks




# # app/api/endpoints/user/audiobook.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, SubscriptionType
from app.core.security import get_current_user
from app.core.config import settings
from app.models.document import Document
from app.utils.s3_utils import s3_handler
from datetime import datetime
import io
from app.schemas.document import DocumentCreate , DocumentFilter, DocumentResponse
#     DocumentUpdate,
#     DocumentResponse,
#     DocumentStats,

from app.services.document_service import  create_and_process_document
from typing import List, Optional
from app.services.document_service import get_documents
# from app.core.config import settings
# from app.database import get_db
# from app.core.security import get_current_user
# from app.models import User,Document
# from app.schemas import DocumentResponse, DocumentCreate
# 




router = APIRouter()

@router.post("/audiobook/upload")
async def upload_pdf_for_audiobook(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF (or image) as a premium user and get an immersive audiobook (Dolby Atmos).

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/audiobook/upload" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN" \
         -F "file=@/path/to/your/document.pdf"
    ```

    **Example Response (Immersive audio):**
    ```json
    {
      "detail": "Audiobook created successfully.",
      "document": {
        "title": "Uploaded Document",
        "author": "Unknown",
        "file_type": "application/pdf",
        "file_key": "audiobook/1/1700000000_document.pdf",
        "is_public": false,
        "url": "https://presigned-url",
        "created_at": "2024-12-20T15:53:55.855Z",
        "description": "Extracted summary",
        "tags": [],
        "detected_language": "English",
        "genre": "Education",
        "processing_status": "completed",
        "processing_error": null,
        "id": 11,
        "user_id": 1,
        "upload_date": "2024-12-20T15:53:55.855Z",
        "file_size": 0,
        "audio_url": "https://presigned-url-to-immersive-audio",
        "audiobook": {
          "id": 6,
          "title": "Uploaded Document",
          "narrator": "Generated Narrator",
          "duration": "0 hours 1 minutes",
          "genre": "Education",
          "publication_date": "2024-12-20T15:53:55.855Z",
          "author": "Unknown",
          "url": "https://presigned-url-to-immersive-audio",
          "is_dolby_atmos_supported": true
        }
      }
    }
    ```
    """
    if current_user.subscription_type != SubscriptionType.premium:
        raise HTTPException(status_code=403, detail="Endpoint reserved for premium users.")

    ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain","application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")

    file_content = await file.read()
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    file_key = f"{settings.S3_FOLDER_NAME}/{current_user.id}/{timestamp}_{file.filename}"

    s3_url = s3_handler.upload_file(
        file_obj=io.BytesIO(file_content),
        bucket=settings.S3_BUCKET_NAME,
        key=file_key,
        content_type=file.content_type
    )
    if not s3_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to S3."
        )

    document_data = DocumentCreate(
        title=file.filename,
        author=current_user.username,
        file_type=file.content_type,
        file_key=file_key,
        url=s3_url,
        is_public=False,
        created_at=datetime.utcnow()
    )

    # Pass subscription_type = "premium"
    document = create_and_process_document(
        db=db,
        document_data=document_data,
        user=current_user,
        file_content=file_content,
        # file_key=file_key,
        # file_size=len(file_content),
        subscription_type="premium",
    )

    return {"detail": "Audiobook created successfully.", "document": document}


@router.get(
    "/audiobook/my_audiobooks",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve My Audiobooks",
    description="""
    Retrieve audiobooks for a premium user.

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/user/audiobook/my_audiobooks" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN"
    ```

    **Example Response:**
    ```json
    [
      {
        "is_public": false,
        "audio_url": "https://visis-audiobooks-data.s3.amazonaws.com/DevIngestion/audio/26/313_processed.mp3?...",
        "title": "Business Open Day pitch structure.pdf",
        "url": "https://visis-audiobooks-data.s3.amazonaws.com/DevIngestion/26/20241224172617_Business%20Open%20Day%20pitch%20structure.pdf?...",
        "file_key": "DevIngestion/26/20241224172617_Business Open Day pitch structure.pdf",
        "id": 313,
        "upload_date": "2024-12-24T17:26:19.302025",
        "detected_language": "English",
        "processing_status": "completed",
        "genre": "Fiction",
        "processing_error": null,
        "created_at": "2024-12-24T17:26:19.301812+00:00",
        "author": "string1",
        "file_size": 75997,
        "file_type": "application/pdf",
        "description": "Structure for 3-mins pitch...",
        "tags": [],
        "audiobook": {
          "id": 6,
          "title": "Business Open Day pitch structure.pdf",
          "narrator": "Generated Narrator",
          "duration": "0 hours 1 minutes",
          "genre": "Fiction",
          "publication_date": "2024-12-24T17:26:19.303Z",
          "author": "string1",
          "url": "https://visis-audiobooks-data.s3.amazonaws.com/DevIngestion/audio/26/313_processed.mp3?...",
          "is_dolby_atmos_supported": true
        }
      }
    ]
    ```
    """
)
def get_my_audiobooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve audiobooks for a premium user.
    """
    if current_user.subscription_type != SubscriptionType.premium:
        raise HTTPException(status_code=403, detail="Endpoint reserved for premium users.")
    
    # Retrieve documents with Audiobook eagerly loaded
    documents = get_documents(
        db=db,
        user_id=current_user.id,
        filter_params=DocumentFilter(),
        skip=0,
        limit=50
    )

    # Filter only those that have an associated Audiobook
    audiobooks = [doc for doc in documents if doc.audiobook]

    return audiobooks
