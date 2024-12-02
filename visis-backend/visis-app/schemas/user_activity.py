# app/schemas/user_activity.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class UserActivityBase(BaseModel):
    activity_type: str
    activity_details: Optional[str] = None

class UserActivityCreate(UserActivityBase):
    pass

class BatchActivityCreate(BaseModel):
    activities: List[UserActivityCreate]

class UserActivityResponse(UserActivityBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ActivityStats(BaseModel):
    total_activities: int
    activity_counts: Dict[str, int]