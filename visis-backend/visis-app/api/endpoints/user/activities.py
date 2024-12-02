# app/api/endpoints/user/activities.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.user_activity import (
    UserActivityCreate,
    UserActivityResponse,
    ActivityStats,
    BatchActivityCreate
)
from app.services.activity_service import ActivityService
from app.core.security import get_current_user

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)

@router.get("/", response_model=List[UserActivityResponse])
async def list_activities(
    activity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    sort_by: str = Query("timestamp", regex="^(timestamp|activity_type)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List activities with filtering and sorting."""
    return await ActivityService.get_activities(
        db,
        user_id=current_user.id,
        activity_type=activity_type,
        start_date=start_date,
        end_date=end_date,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=UserActivityResponse)
async def create_activity(
    activity: UserActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new activity."""
    return await ActivityService.create_activity(
        db,
        user_id=current_user.id,
        activity=activity
    )

@router.post("/batch", response_model=List[UserActivityResponse])
async def create_batch_activities(
    activities: BatchActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple activities at once."""
    return await ActivityService.create_batch_activities(
        db,
        user_id=current_user.id,
        activities=activities.activities
    )

@router.get("/stats", response_model=ActivityStats)
async def get_activity_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get activity statistics."""
    return await ActivityService.get_stats(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/recent", response_model=List[UserActivityResponse])
async def get_recent_activities(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent activities."""
    start_date = datetime.utcnow() - timedelta(hours=hours)
    return await ActivityService.get_activities(
        db,
        user_id=current_user.id,
        start_date=start_date,
        sort_by="timestamp",
        sort_order="desc",
        limit=50
    )

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an activity."""
    await ActivityService.delete_activity(
        db,
        activity_id=activity_id,
        user_id=current_user.id
    )