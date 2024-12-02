from pydantic import BaseModel
from datetime import datetime

class FeedbackBase(BaseModel):
    feedback_type: str
    content: str
    submission_date: datetime

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


