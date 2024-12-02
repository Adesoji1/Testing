from pydantic import BaseModel
from datetime import datetime

class AppSettingBase(BaseModel):
    name: str
    value: str
    last_updated: datetime

class AppSettingCreate(AppSettingBase):
    pass

class AppSettingResponse(AppSettingBase):
    id: int

    class Config:
        from_attributes = True