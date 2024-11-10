
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.user_bookmark import UserBookmark
from app.models.document import Document
from app.models.audiobook import Audiobook
from app.schemas.user_bookmark import UserBookmarkCreate, UserBookmarkResponse
from app.core.security import get_current_user

router = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=UserBookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    bookmark: UserBookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bookmark for the current user."""
    # Ensure at least one of document_id or audiobook_id is provided
    if bookmark.document_id is None and bookmark.audiobook_id is None:
        raise HTTPException(status_code=400, detail="Either document_id or audiobook_id must be provided")

    # Validate document_id and audiobook_id
    if bookmark.document_id is not None:
        document = db.query(Document).filter(Document.id == bookmark.document_id).first()
        if not document:
            raise HTTPException(status_code=400, detail="Invalid document_id")
        # Find the corresponding audiobook
        audiobook = db.query(Audiobook).filter(Audiobook.document_id == bookmark.document_id).first()
        if audiobook:
            bookmark.audiobook_id = audiobook.id

    if bookmark.audiobook_id is not None:
        audiobook = db.query(Audiobook).filter(Audiobook.id == bookmark.audiobook_id).first()
        if not audiobook:
            raise HTTPException(status_code=400, detail="Invalid audiobook_id")

    db_bookmark = UserBookmark(**bookmark.dict(), user_id=current_user.id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.get("/", response_model=List[UserBookmarkResponse])
def read_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all bookmarks for the current user."""
    bookmarks = db.query(UserBookmark).filter(UserBookmark.user_id == current_user.id).all()
    return bookmarks

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a bookmark by ID for the current user."""
    bookmark = db.query(UserBookmark).filter(
        UserBookmark.id == bookmark_id,
        UserBookmark.user_id == current_user.id
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return {"detail": "Bookmark deleted successfully"}