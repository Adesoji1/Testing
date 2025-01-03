# app/schemas/document_filter.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DocumentFilter(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    file_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
