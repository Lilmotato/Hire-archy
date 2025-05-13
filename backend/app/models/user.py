from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdateSchema(BaseModel):
    full_name: Optional[str]
    phone_number: Optional[str]
    location: Optional[str]
    years_of_experience: Optional[int]
    key_skills: Optional[list[str]]

    
class UserProfileResponse(BaseModel):
    uid: str
    email: EmailStr
    full_name: str | None = None
    phone_number: str | None = None
    role: str
    resume_url: str | None = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class CandidateSearchResponse(UserProfileResponse):
    location: Optional[str] = None
    years_of_experience: Optional[int] = None
    key_skills: Optional[list[str]] = None