from pydantic import BaseModel
from datetime import datetime

class ScanningHistoryBase(BaseModel):
    scan_type: str
    scan_content: str
    scan_date: datetime

class ScanningHistoryCreate(ScanningHistoryBase):
    pass

class ScanningHistoryResponse(ScanningHistoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True