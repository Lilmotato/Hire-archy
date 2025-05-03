from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    

# For recruiter to view user profile
class UserProfileResponse(BaseModel):
    uid: str
    email: EmailStr
    full_name: str | None = None
    phone_number: str | None = None
    role: str
    resume_url: str | None = None
    created_at: str | None = None  # or datetime if you prefer

    class Config:
        orm_mode = True
