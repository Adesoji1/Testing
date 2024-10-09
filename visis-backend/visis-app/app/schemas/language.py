from pydantic import BaseModel

class LanguageBase(BaseModel):
    name: str
    code: str

class LanguageCreate(LanguageBase):
    pass

class LanguageResponse(LanguageBase):
    id: int

    class Config:
        from_attributes = True