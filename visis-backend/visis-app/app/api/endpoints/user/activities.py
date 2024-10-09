from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import UserActivity, User
from app.schemas.user_activity import UserActivityCreate, UserActivityResponse
from app.database import SessionLocal
from app.core.security import get_current_user

router = APIRouter(
    prefix="/activities",
    tags=["activities"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UserActivityResponse])
def list_activities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    activities = db.query(UserActivity).filter(UserActivity.username == current_user.username).offset(skip).limit(limit).all()
    return activities

@router.post("/", response_model=UserActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(activity: UserActivityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_activity = UserActivity(**activity.dict(), username=current_user.username)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    activity = db.query(UserActivity).filter(UserActivity.username == activity_id, UserActivity.username == current_user.username).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(activity)
    db.commit()
    return {"detail": "Activity deleted successfully"}