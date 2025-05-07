from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base
    
class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    key_skills = Column(ARRAY(String), nullable=False)
    experience_required = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    recruiter_id = Column(String, nullable=False)
    job_summary = Column(String, nullable=True)

    # New fields
    embedding = Column(Vector(1536))  # For matching candidates to job
    applied_user_ids = Column(ARRAY(Integer), default=[])  # Recruiter candidate pool