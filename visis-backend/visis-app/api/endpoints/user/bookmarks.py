#app/api/endpoints/user/bookmarks.py


from fastapi import APIRouter, Depends, HTTPException, status, Query,Response
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.document import Document
from app.models.audiobook import Audiobook  # Ensure you import the Audiobook model
from app.models.user import User
from app.models.user_bookmark import UserBookmark
from app.schemas.user_bookmark import (
    UserBookmarkCreate,
    UserBookmarkResponse,
    UserBookmarkUpdate,
    BookmarkListResponse,
)
from app.core.security import get_current_user

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
    # Fetch the document based on the document_id
    document = db.query(Document).filter(Document.id == bookmark_data.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Create a new bookmark
    new_bookmark = UserBookmark(
        user_id=user.id,
        document_id=bookmark_data.document_id,
        title=bookmark_data.title,
        timestamp=bookmark_data.timestamp,
        position=bookmark_data.position,
    )

    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)

    # Add the audio_url from the document
    new_bookmark.audio_url = document.audio_url  # Assuming audio_url is stored in Document

    db.commit()

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
    # Fetch bookmarks from the database, eagerly loading related document and audiobook
    bookmarks = (
        db.query(UserBookmark)
        .filter(UserBookmark.user_id == user.id)
        .options(joinedload(UserBookmark.document))
        .options(joinedload(UserBookmark.audiobook))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Set audio_url for each bookmark
    for bookmark in bookmarks:
        if bookmark.document:
            bookmark.audio_url = bookmark.document.audio_url
        elif bookmark.audiobook:
            bookmark.audio_url = bookmark.audiobook.audio_url
        else:
            bookmark.audio_url = None

    # Convert UserBookmark SQLAlchemy models to UserBookmarkResponse Pydantic models
    bookmark_responses = [UserBookmarkResponse.from_orm(bookmark) for bookmark in bookmarks]

    # Return the response in the required format
    return BookmarkListResponse(
        total=len(bookmark_responses),
        skip=skip,
        limit=limit,
        bookmarks=bookmark_responses,
    )


# Update Bookmark

@router.put("/{bookmark_id}", response_model=UserBookmarkResponse)
def update_bookmark(
    bookmark_id: int,
    bookmark_data: UserBookmarkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing bookmark with position and timestamp.
    """
    # Eagerly load related Document and Audiobook
    bookmark = (
        db.query(UserBookmark)
        .filter(UserBookmark.id == bookmark_id, UserBookmark.user_id == user.id)
        .options(joinedload(UserBookmark.document))
        .options(joinedload(UserBookmark.audiobook))
        .first()
    )

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    # Update the bookmark fields as necessary
    if bookmark_data.timestamp is not None:
        bookmark.timestamp = bookmark_data.timestamp
    if bookmark_data.title is not None:
        bookmark.title = bookmark_data.title

    db.commit()
    db.refresh(bookmark)

    # Set the audio_url from the related Document or Audiobook
    if bookmark.document:
        bookmark.audio_url = bookmark.document.audio_url
    elif bookmark.audiobook:
        bookmark.audio_url = bookmark.audiobook.audio_url
    else:
        bookmark.audio_url = None

    # No need to commit again since audio_url is not a DB column

    return bookmark

# Delete Bookmark
@router.delete("/{bookmark_id}", status_code=status.HTTP_200_OK)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a bookmark by its ID.
    """
    bookmark = (
        db.query(UserBookmark)
        .filter(UserBookmark.id == bookmark_id, UserBookmark.user_id == user.id)
        .first()
    )

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()
    return {"detail": "Bookmark deleted successfully."}



# Retrieve Last Bookmark for an Audiobook
@router.get("/resume", response_model=UserBookmarkResponse)
def get_last_bookmark(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve the last bookmark for the current user.
    """
    bookmark = (
        db.query(UserBookmark)
        .filter(UserBookmark.user_id == user.id)
        .options(joinedload(UserBookmark.document))
        .options(joinedload(UserBookmark.audiobook))
        .order_by(UserBookmark.created_at.desc())
        .first()
    )

    if not bookmark:
        raise HTTPException(status_code=404, detail="No bookmark found")

    # Set the audio_url
    if bookmark.document:
        bookmark.audio_url = bookmark.document.audio_url
    elif bookmark.audiobook:
        bookmark.audio_url = bookmark.audiobook.audio_url
    else:
        bookmark.audio_url = None

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
    Update the last position of an audiobook for the current user based on the last bookmark.
    """
    # Get the bookmark for the given audiobook
    bookmark = (
        db.query(UserBookmark)
        .filter(
            UserBookmark.user_id == user.id,
            UserBookmark.audiobook_id == audiobook_id,
        )
        .options(joinedload(UserBookmark.audiobook))
        .first()
    )

    if not bookmark:
        # Create a new bookmark
        bookmark = UserBookmark(
            user_id=user.id,
            audiobook_id=audiobook_id,
            position=position,
            timestamp=datetime.utcnow().strftime("%H:%M:%S"),
        )
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
    else:
        # Update the position and timestamp of the existing bookmark
        bookmark.position = position
        bookmark.timestamp = datetime.utcnow().strftime("%H:%M:%S")
        db.commit()
        db.refresh(bookmark)

    # Set the audio_url
    if bookmark.audiobook:
        bookmark.audio_url = bookmark.audiobook.audio_url
    else:
        bookmark.audio_url = None

    return bookmark


