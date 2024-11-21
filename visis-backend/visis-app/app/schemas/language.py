# #app/schemas/language.py
# from pydantic import BaseModel

# class LanguageBase(BaseModel):
#     name: str
#     code: str

# class LanguageCreate(LanguageBase):
#     pass

# class LanguageResponse(LanguageBase):
#     id: int

#     class Config:
#         from_attributes = True


# app/schemas/language.py
from pydantic import BaseModel
from typing import List

class LanguageBase(BaseModel):
    name: str
    code: str

class LanguageCreate(LanguageBase):
    pass

class LanguageResponse(LanguageBase):
    id: int
    voices: List[str] = []

    class Config:
        orm_mode = True

class DetectLanguageResponse(BaseModel):
    language_code: str
    voice_id: str
