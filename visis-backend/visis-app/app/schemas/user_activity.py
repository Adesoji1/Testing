# from pydantic import BaseModel
# from datetime import datetime

# class UserActivityBase(BaseModel):
#     activity_type: str
#     activity_details: str
#     timestamp: datetime

# class UserActivityCreate(UserActivityBase):
#     pass

# class UserActivityResponse(UserActivityBase):
#     id: int
#     user_id: int

#     class Config:
#         from_attributes = True


# schemas/user_activity.py

# from pydantic import BaseModel
# from datetime import datetime
# from typing import Optional

# class UserActivityBase(BaseModel):
#     activity_type: str
#     activity_details: Optional[str] = None

# class UserActivityCreate(UserActivityBase):
#     pass

# class UserActivityResponse(UserActivityBase):
#     id: int
#     user_id: int
#     timestamp: datetime

#     model_config = {
#         "from_attributes": True
#     }



from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserActivityBase(BaseModel):
    activity_type: str
    activity_details: Optional[str] = None

class UserActivityCreate(UserActivityBase):
    pass

class UserActivityResponse(UserActivityBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
