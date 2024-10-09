from pydantic import BaseModel
from datetime import datetime

class UserActivityBase(BaseModel):
    activity_type: str
    activity_details: str
    timestamp: datetime

class UserActivityCreate(UserActivityBase):
    pass

class UserActivityResponse(UserActivityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True