from pydantic import BaseModel
from uuid import UUID

class MatchScoreOut(BaseModel):
    job_id: UUID
    score: float

    class Config:
        orm_mode = True
