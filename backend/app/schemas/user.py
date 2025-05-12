# models/user.py
from sqlalchemy import ARRAY, Boolean, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(20))
    role = Column(String(20), nullable=False)
    resume_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # pgvector
    key_skills = Column(ARRAY(String), default=[])
    location = Column(String)
    years_of_experience = Column(Integer)
    embedding = Column(Vector(1536))  #For semantic search
    profile_completed = Column(Boolean, default=False)
    