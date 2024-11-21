#app/api/endpoints/user/bookmarks.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.user_bookmark import UserBookmark
from app.models.document import Document
from app.models.audiobook import Audiobook
from app.schemas.user_bookmark import (
    UserBookmarkCreate,
    UserBookmarkResponse,
    UserBookmarkUpdate,
    BookmarkListResponse
)
from app.core.security import get_current_user
from app.services.bookmark_services import get_bookmarks
from datetime import datetime

router = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"],
    responses={404: {"description": "Not found"}},
)

# Create Bookmark
@router.post("/", response_model=UserBookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    bookmark_data: UserBookmarkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Create the bookmark with mutual exclusivity handled by the Pydantic root_validator

    # Assign the current timestamp if not provided
    if not bookmark_data.timestamp:
        bookmark_data.timestamp = datetime.utcnow().isoformat()  # Assign current UTC time

    # Initialize the bookmark with user_id and position
    new_bookmark = UserBookmark(
        user_id=user.id,
        document_id=bookmark_data.document_id,
        audiobook_id=bookmark_data.audiobook_id,
        position=bookmark_data.position,
        timestamp=bookmark_data.timestamp
        # Do not set `date_created` here; let SQLAlchemy handle it
    )

    # If it's an audiobook bookmark
    if bookmark_data.audiobook_id is not None:
        audiobook = db.query(Audiobook).filter_by(id=bookmark_data.audiobook_id).first()
        if not audiobook:
            raise HTTPException(status_code=404, detail="Audiobook not found.")
        new_bookmark.audiobook_id = bookmark_data.audiobook_id

    # If it's a document bookmark
    if bookmark_data.document_id is not None:
        document = db.query(Document).filter_by(id=bookmark_data.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        new_bookmark.document_id = bookmark_data.document_id

    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)
    return new_bookmark

# List Bookmarks with Pagination
@router.get("/", response_model=BookmarkListResponse)
def list_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve all bookmarks for the current user with pagination.
    """
    total, bookmarks = get_bookmarks(db=db, user_id=user.id, skip=skip, limit=limit)
    return BookmarkListResponse(
        total=total,
        skip=skip,
        limit=limit,
        bookmarks=bookmarks,
    )

# Update Bookmark
@router.put("/{bookmark_id}", response_model=UserBookmarkResponse, status_code=status.HTTP_200_OK)
def update_bookmark(
    bookmark_id: int,
    bookmark_data: UserBookmarkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing bookmark.
    """
    bookmark = db.query(UserBookmark).filter(
        UserBookmark.id == bookmark_id, UserBookmark.user_id == user.id
    ).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found.")

    # Ensure that document_id and audiobook_id remain mutually exclusive
    if bookmark_data.document_id is not None and bookmark_data.audiobook_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either 'document_id' or 'audiobook_id', but not both."
        )

    # Update position if provided
    if bookmark_data.position is not None:
        bookmark.position = bookmark_data.position

    # Update document_id if provided
    if bookmark_data.document_id is not None:
        # Clear audiobook_id if setting document_id
        bookmark.audiobook_id = None
        document = db.query(Document).filter_by(id=bookmark_data.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        bookmark.document_id = bookmark_data.document_id

    # Update audiobook_id if provided
    if bookmark_data.audiobook_id is not None:
        # Clear document_id if setting audiobook_id
        bookmark.document_id = None
        audiobook = db.query(Audiobook).filter_by(id=bookmark_data.audiobook_id).first()
        if not audiobook:
            raise HTTPException(status_code=404, detail="Audiobook not found.")
        bookmark.audiobook_id = bookmark_data.audiobook_id

    db.commit()
    db.refresh(bookmark)
    return bookmark

# Delete Bookmark
@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a bookmark by its ID.
    """
    bookmark = db.query(UserBookmark).filter(
        UserBookmark.id == bookmark_id, UserBookmark.user_id == user.id
    ).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found.")

    db.delete(bookmark)
    db.commit()
    return {"detail": "Bookmark deleted successfully."}

# Retrieve Last Bookmark for an Audiobook
@router.get("/resume/{audiobook_id}", response_model=UserBookmarkResponse)
def get_last_bookmark(
    audiobook_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve the last bookmark for an audiobook.
    """
    bookmark = db.query(UserBookmark).filter(
        UserBookmark.audiobook_id == audiobook_id,
        UserBookmark.user_id == user.id,
    ).order_by(UserBookmark.created_at.desc()).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="No bookmark found.")

    return bookmark

# Update Last Position (For Audiobooks)
@router.post("/last-position", response_model=UserBookmarkResponse, status_code=status.HTTP_200_OK)
def update_last_position(
    audiobook_id: int,
    position: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update the last position of an audiobook for the current user.
    """
    bookmark = db.query(UserBookmark).filter(
        UserBookmark.audiobook_id == audiobook_id,
        UserBookmark.user_id == user.id
    ).order_by(UserBookmark.created_at.desc()).first()

    if not bookmark:
        # Create a new bookmark if none exists
        bookmark = UserBookmark(
            user_id=user.id,
            audiobook_id=audiobook_id,
            position=position,
        )
        db.add(bookmark)
    else:
        # Update the position of the existing bookmark
        bookmark.position = position

    db.commit()
    db.refresh(bookmark)
    return bookmark
