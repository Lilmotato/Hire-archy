from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# 🚫 Recruiter ID & job_summary are set by backend, not user
class JobListingCreate(BaseModel):
    title: str = Field(..., example="Senior Backend Engineer")
    description: str = Field(..., example="Work on scalable backend systems...")
    key_skills: List[str] = Field(..., example=["FastAPI", "PostgreSQL", "Docker"])
    experience_required: int = Field(..., ge=0, example=3)
    location: str = Field(..., example="Bangalore")
    company_name: str = Field(..., example="TechCorp")


# ✅ Used for PATCH endpoint
class JobListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    key_skills: Optional[List[str]] = None
    experience_required: Optional[int] = None
    location: Optional[str] = None
    company_name: Optional[str] = None


# ✅ Full output model with metadata
class JobListingOut(BaseModel):
    id: UUID
    title: str
    description: str
    key_skills: List[str]
    experience_required: int
    location: str
    company_name: str
    is_active: bool
    recruiter_id: str
    job_summary: Optional[str]

    class Config:
        orm_mode = True
