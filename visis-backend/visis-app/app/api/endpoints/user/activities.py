#app/api/endpoints/user/activities.py


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user_activity import UserActivityCreate, UserActivityResponse
from app.services.activity_service import log_user_activity, get_user_activities, delete_user_activity
from app.core.security import get_current_user

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[UserActivityResponse])
def list_activities(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List activities for the current user with pagination.
    """
    return get_user_activities(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/", response_model=UserActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: UserActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Log a new activity for the current user.
    """
    return log_user_activity(db, user_id=current_user.id, activity_type=activity.activity_type, activity_details=activity.activity_details)

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an activity by ID for the current user.
    """
    try:
        delete_user_activity(db, activity_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
