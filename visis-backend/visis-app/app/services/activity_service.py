# app/services/activity_service.py

# from sqlalchemy.orm import Session
# from app.models.user_activity import UserActivity

# def log_user_activity(db: Session, user_id: int, activity_type: str, activity_details: str = None):
#     activity = UserActivity(
#         user_id=user_id,
#         activity_type=activity_type,
#         activity_details=activity_details,
#     )
#     db.add(activity)
#     db.commit()


from sqlalchemy.orm import Session
from app.models.user_activity import UserActivity

def log_user_activity(db: Session, user_id: int, activity_type: str, activity_details: str = None):
    """
    Log a new user activity.
    """
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        activity_details=activity_details,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

def get_user_activities(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Retrieve activities for a given user with pagination.
    """
    return db.query(UserActivity).filter(UserActivity.user_id == user_id).offset(skip).limit(limit).all()

def delete_user_activity(db: Session, activity_id: int):
    """
    Delete a user activity by ID.
    """
    activity = db.query(UserActivity).filter(UserActivity.id == activity_id).first()
    if not activity:
        raise ValueError(f"Activity with ID {activity_id} not found.")
    db.delete(activity)
    db.commit()
    return activity
