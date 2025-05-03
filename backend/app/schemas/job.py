from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str = Field(..., example="Senior Backend Engineer")
    description: str = Field(..., example="Looking for a skilled backend engineer...")
    location: str = Field(..., example="Remote")
    salary_range: Optional[str] = Field(None, example="10-20 LPA")
    company_name: str = Field(..., example="TechCorp")

class JobInDB(JobCreate):
    id: str = Field(..., alias="_id")
    recruiter_id: str
    job_summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
