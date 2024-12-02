from pydantic import BaseModel

class DocumentLanguageBase(BaseModel):
    document_id: int
    language_id: int

class DocumentLanguageCreate(DocumentLanguageBase):
    pass

class DocumentLanguageResponse(DocumentLanguageBase):
    id: int

    class Config:
        from_attributes = True