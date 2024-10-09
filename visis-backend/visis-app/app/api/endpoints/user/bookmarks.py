from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import UserBookmark, User
from app.schemas.user_bookmark import UserBookmarkCreate, UserBookmarkResponse
from app.database import SessionLocal
from app.core.security import get_current_user

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UserBookmarkResponse])
def list_bookmarks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookmarks = db.query(UserBookmark).filter(UserBookmark.user_id == current_user.id).offset(skip).limit(limit).all()
    return bookmarks

@router.post("/", response_model=UserBookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(bookmark: UserBookmarkCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_bookmark = UserBookmark(**bookmark.dict(), user_id=current_user.id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookmark = db.query(UserBookmark).filter(UserBookmark.id == bookmark_id, UserBookmark.user_id == current_user.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return {"detail": "Bookmark deleted successfully"}