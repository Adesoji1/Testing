# #Visiszipnov26/app/api/endpoints/user/pdfreader.py
# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
# from sqlalchemy.orm import Session
# from datetime import datetime
# import io

# from app.database import get_db
# from app.models.user import User, SubscriptionType
# from app.core.security import get_current_user
# from app.core.config import settings
# from app.schemas.document import DocumentCreate,DocumentFilter
# from app.utils.s3_utils import s3_handler
# from app.services.document_service import create_document
# import logging
# from typing import List
# # from app.core.config import settings
# # from app.database import get_db
# # from app.core.security import get_current_user
# # from app.models import User,Document
# from app.schemas import DocumentResponse, DocumentCreate


# logger = logging.getLogger(__name__)
# router = APIRouter()


# @router.post("/pdfreader/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, summary="Upload PDF (Free Users)")
# async def upload_pdf(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Upload a document (PDF or image) as a free user, convert to audiobook without immersive effects.

#     **Example Request:**
#     ```bash
#     curl -X POST "http://localhost:8000/user/pdfreader/upload" \
#          -H "Authorization: Bearer YOUR_JWT_TOKEN" \
#          -F "file=@/path/to/your/document.pdf"
#     ```

#     **Example Response (No immersive audio):**
#     ```json
#     {
#       "detail": "PDF uploaded successfully.",
#       "document": {
#         "title": "Uploaded Document",
#         "author": "Unknown",
#         "file_type": "application/pdf",
#         "file_key": "pdfreader/1/1700000000_document.pdf",
#         "is_public": false,
#         "url": "https://presigned-url",
#         "created_at": "2024-12-20T15:53:55.855Z",
#         "description": "Extracted summary",
#         "tags": [],
#         "detected_language": "English",
#         "genre": "Education",
#         "processing_status": "completed",
#         "processing_error": null,
#         "id": 10,
#         "user_id": 1,
#         "upload_date": "2024-12-20T15:53:55.855Z",
#         "file_size": 0,
#         "audio_url": "https://presigned-url-to-audio",
#         "audiobook": {
#           "id": 5,
#           "title": "Uploaded Document",
#           "narrator": "Generated Narrator",
#           "duration": "0 hours 1 minutes",
#           "genre": "Education",
#           "publication_date": "2024-12-20T15:53:55.855Z",
#           "author": "Unknown",
#           "url": "https://presigned-url-to-audio",
#           "is_dolby_atmos_supported": false
#         }
#       }
#     }
#     ```
#     """
#     if current_user.subscription_type != SubscriptionType.free:
#         raise HTTPException(status_code=403, detail="Endpoint reserved for free users.")

#     ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain","application/vnd.openxmlformats-officedocument.wordprocessingml.document",]
#     if file.content_type not in ALLOWED_CONTENT_TYPES:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")

#     file_content = await file.read()
#     from app.services.document_service import count_user_pdfs
#     user_pdfs_count = count_user_pdfs(db, current_user.id)
#     if file.content_type == "application/pdf" and user_pdfs_count >= 13:
#         raise HTTPException(status_code=400, detail="Free users can only upload up to 13 PDFs.")

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

#     # Pass subscription_type = "free"
#     document = create_document(
#         db=db,
#         document_data=document_data,
#         user_id=current_user.id,
#         file_key=file_key,
#         file_size=len(file_content),
#         subscription_type="free"
#     )

#     return  document


# @router.get("/pdfreader/my_pdfs", response_model=List[DocumentResponse])
# def get_my_pdfs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

#     """
#     Retrieve PDFs of a free user.

#     **Example Request:**
#     ```bash
#     curl -X GET "http://localhost:8000/user/pdfreader/my_pdfs" -H "Authorization: Bearer YOUR_JWT_TOKEN"
#     ```

#     **Example Response:**
#     ```json
#     {
#       "pdfs": [
#         {
#           "id": 10,
#           "title": "Uploaded Document",
#           "file_type": "application/pdf",
#           "audio_url": "https://presigned-url-to-audio",
#           "audiobook": {
#             "is_dolby_atmos_supported": false
#           }
#         }
#       ]
#     }
#     ```
#     """
#     if current_user.subscription_type != SubscriptionType.free:
#         raise HTTPException(status_code=403, detail="Endpoint reserved for free users.")
#     from app.services.document_service import get_documents
#     documents = get_documents(db, user_id=current_user.id, filter_params=DocumentFilter(), skip=0, limit=50)
#     return documents



#Visiszipnov26/app/api/endpoints/user/pdfreader.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from datetime import datetime
import io

from app.database import get_db
from app.models.user import User, SubscriptionType
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.document import DocumentCreate,DocumentFilter
from app.utils.s3_utils import s3_handler
from app.services.document_service import create_and_process_document
import logging
from typing import List
# from app.core.config import settings
# from app.database import get_db
# from app.core.security import get_current_user
# from app.models import User,Document
from app.schemas import DocumentResponse, DocumentCreate


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/pdfreader/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, summary="Upload PDF (Free Users)")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document (PDF or image) as a free user, convert to audiobook without immersive effects.

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/user/pdfreader/upload" \
         -H "Authorization: Bearer YOUR_JWT_TOKEN" \
         -F "file=@/path/to/your/document.pdf"
    ```

    **Example Response (No immersive audio):**
    ```json
    {
      "detail": "PDF uploaded successfully.",
      "document": {
        "title": "Uploaded Document",
        "author": "Unknown",
        "file_type": "application/pdf",
        "file_key": "pdfreader/1/1700000000_document.pdf",
        "is_public": false,
        "url": "https://presigned-url",
        "created_at": "2024-12-20T15:53:55.855Z",
        "description": "Extracted summary",
        "tags": [],
        "detected_language": "English",
        "genre": "Education",
        "processing_status": "completed",
        "processing_error": null,
        "id": 10,
        "user_id": 1,
        "upload_date": "2024-12-20T15:53:55.855Z",
        "file_size": 0,
        "audio_url": "https://presigned-url-to-audio",
        "audiobook": {
          "id": 5,
          "title": "Uploaded Document",
          "narrator": "Generated Narrator",
          "duration": "0 hours 1 minutes",
          "genre": "Education",
          "publication_date": "2024-12-20T15:53:55.855Z",
          "author": "Unknown",
          "url": "https://presigned-url-to-audio",
          "is_dolby_atmos_supported": false
        }
      }
    }
    ```
    """
    if current_user.subscription_type != SubscriptionType.free:
        raise HTTPException(status_code=403, detail="Endpoint reserved for free users.")

    ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg", "text/plain","application/vnd.openxmlformats-officedocument.wordprocessingml.document",]
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")

    file_content = await file.read()
    from app.services.document_service import count_user_pdfs
    user_pdfs_count = count_user_pdfs(db, current_user.id)
    if file.content_type == "application/pdf" and user_pdfs_count == 57:
        raise HTTPException(status_code=400, detail="Free users can only upload up to 57 PDFs.")

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

    # Pass subscription_type = "free"
    document = create_and_process_document(
        db=db,
        document_data=document_data,
        user=current_user,
        # file_key=file_key,
        file_content=file_content,
        # file_size=len(file_content),
        subscription_type="free",
    )

    return  document


@router.get("/pdfreader/my_pdfs", response_model=List[DocumentResponse])
def get_my_pdfs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    """
    Retrieve PDFs of a free user.

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/user/pdfreader/my_pdfs" -H "Authorization: Bearer YOUR_JWT_TOKEN"
    ```

    **Example Response:**
    ```json
    {
      "pdfs": [
        {
          "id": 10,
          "title": "Uploaded Document",
          "file_type": "application/pdf",
          "audio_url": "https://presigned-url-to-audio",
          "audiobook": {
            "is_dolby_atmos_supported": false
          }
        }
      ]
    }
    ```
    """
    if current_user.subscription_type != SubscriptionType.free:
        raise HTTPException(status_code=403, detail="Endpoint reserved for free users.")
    from app.services.document_service import get_documents
    documents = get_documents(db, user_id=current_user.id, filter_params=DocumentFilter(), skip=0, limit=50)
    return documents