from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdateKeys(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_places_api_key: Optional[str] = None

class User(UserBase):
    id: int
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_places_api_key: Optional[str] = None

    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    name: str
    address: Optional[str] = None
    url: str
    phone: Optional[str] = None
    reviews_count: Optional[int] = 0

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    status: str
    score_total: Optional[int] = None
    score_details: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class FindLeadsRequest(BaseModel):
    branche: str
    ort: str
    radius: Optional[int] = 2000
