# app/services/activity_service.py

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.user_activity import UserActivity
from app.schemas.user_activity import UserActivityCreate, ActivityStats

class ActivityService:
    @staticmethod
    async def get_activities(
        db: Session,
        user_id: int,
        activity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 10
    ) -> List[UserActivity]:
        query = db.query(UserActivity).filter(UserActivity.user_id == user_id)

        if activity_type:
            query = query.filter(UserActivity.activity_type == activity_type)
        if start_date:
            query = query.filter(UserActivity.timestamp >= start_date)
        if end_date:
            query = query.filter(UserActivity.timestamp <= end_date)
        if search:
            query = query.filter(UserActivity.activity_details.ilike(f"%{search}%"))

        order_col = getattr(UserActivity, sort_by)
        if sort_order == "desc":
            order_col = order_col.desc()
        
        return query.order_by(order_col).offset(skip).limit(limit).all()

    @staticmethod
    async def create_activity(
        db: Session,
        user_id: int,
        activity: UserActivityCreate
    ) -> UserActivity:
        db_activity = UserActivity(
            user_id=user_id,
            activity_type=activity.activity_type,
            activity_details=activity.activity_details
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    @staticmethod
    async def create_batch_activities(
        db: Session,
        user_id: int,
        activities: List[UserActivityCreate]
    ) -> List[UserActivity]:
        db_activities = [
            UserActivity(
                user_id=user_id,
                activity_type=activity.activity_type,
                activity_details=activity.activity_details
            )
            for activity in activities
        ]
        db.add_all(db_activities)
        db.commit()
        for activity in db_activities:
            db.refresh(activity)
        return db_activities

    @staticmethod
    async def get_stats(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ActivityStats:
        query = db.query(
            UserActivity.activity_type,
            func.count(UserActivity.id).label('count')
        ).filter(UserActivity.user_id == user_id)

        if start_date:
            query = query.filter(UserActivity.timestamp >= start_date)
        if end_date:
            query = query.filter(UserActivity.timestamp <= end_date)

        results = query.group_by(UserActivity.activity_type).all()
        
        return ActivityStats(
            total_activities=sum(count for _, count in results),
            activity_counts={activity_type: count for activity_type, count in results}
        )

    @staticmethod
    async def delete_activity(db: Session, activity_id: int, user_id: int) -> None:
        activity = db.query(UserActivity).filter(
            UserActivity.id == activity_id,
            UserActivity.user_id == user_id
        ).first()
        
        if not activity:
            raise HTTPException(
                status_code=404,
                detail=f"Activity {activity_id} not found"
            )
        
        db.delete(activity)
        db.commit()