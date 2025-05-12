from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from services.search import filter_candidates
from models.user import CandidateSearchResponse

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.get("/", response_model=List[CandidateSearchResponse])
async def get_candidates_by_filters(
    skills: Optional[List[str]] = Query(None),
    location: Optional[str] = None,
    min_experience: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    return await filter_candidates(skills, location, min_experience, db)
