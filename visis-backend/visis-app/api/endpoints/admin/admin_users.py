from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import User
from app.schemas.user import UserResponse
from app.database import SessionLocal
from app.core.security import get_current_user, oauth2_scheme
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.token import TokenData
from app.core.security import get_current_admin_user

router = APIRouter(
    prefix="/admin/users",
    tags=["admin-users"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}