from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    key_skills = Column(ARRAY(String), nullable=False)  # Requires PostgreSQL
    experience_required = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    is_remote = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
