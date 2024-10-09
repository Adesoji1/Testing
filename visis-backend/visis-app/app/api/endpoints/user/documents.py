from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models import Document, User
from app.schemas.document import DocumentCreate, DocumentResponse
from app.database import SessionLocal
from app.core.security import get_current_user
from app.services.document_service import create_document, get_documents, delete_document
from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings

# Initialize router for document-related routes
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: str | None = None



# Dependency to get the current user
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user

# Route to list documents
@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
async def list_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    documents = get_documents(db, skip=skip, limit=limit)
    return documents

# Route to upload a document
@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file_location = f"files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    document = DocumentCreate(
        title=file.filename,
        author=user.username,
        file_type=file.content_type,
        file_path=file_location,
        is_public=False
    )
    return create_document(db, document, user.id)

# Route to delete a document by ID
@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not delete_document(db, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"detail": "Document deleted successfully"}