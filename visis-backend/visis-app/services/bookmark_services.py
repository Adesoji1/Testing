# app/services/bookmark_service.py
# from sqlalchemy.orm import Session
# from app.models.user_bookmark import UserBookmark

# def get_bookmarks(db: Session, user_id: int, skip: int = 0, limit: int = 10):
#     """
#     Retrieve bookmarks for a user with pagination.
#     Returns the total count and a list of bookmarks.
#     """
#     query = db.query(UserBookmark).filter(UserBookmark.user_id == user_id)
#     total = query.count()
#     bookmarks = query.offset(skip).limit(limit).all()
#     for bookmark in bookmarks:
#         print(f"Bookmark ID: {bookmark.id}, Created At: {bookmark.created_at}")
#     return total, bookmarks


# def get_bookmarks(db: Session, user_id: int, skip: int = 0, limit: int = 10):
 
#     query = db.query(UserBookmark).filter(UserBookmark.user_id == user_id)
#     total = query.count()
#     bookmarks = query.offset(skip).limit(limit).all()
#     return total, bookmarks

from sqlalchemy.orm import Session
from app.models.user_bookmark import UserBookmark

def get_bookmarks(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    query = db.query(UserBookmark).filter(UserBookmark.user_id == user_id)
    total = query.count()
    bookmarks = query.offset(skip).limit(limit).all()
    return total, bookmarks
