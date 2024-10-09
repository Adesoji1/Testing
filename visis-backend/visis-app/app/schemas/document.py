from pydantic import BaseModel
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    author: str
    file_type: str
    file_path: str
    is_public: bool
    url: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    upload_date: datetime

    class Config:
        # orm_mode = True
        from_attributes = True