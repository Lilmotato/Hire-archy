from sqlalchemy import Column, Float, ForeignKey, String, UniqueConstraint
from db.database import Base
from sqlalchemy.dialects.postgresql import UUID

class MatchScore(Base):
    __tablename__ = "match_scores"

    id = Column(UUID(as_uuid=True), primary_key=True)
    uid = Column(String, ForeignKey("users.uid"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_listings.id"), nullable=False)
    score = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("uid", "job_id", name="uq_uid_job"),
    )
