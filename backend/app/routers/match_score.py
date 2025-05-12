from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.firebase import get_current_user
from db.database import get_db
from services.match_score_service import recommend_jobs
from models.match_score import MatchScoreOut

router = APIRouter(prefix="/match-scores", tags=["Match Scores"])

@router.get("/recommendations/{uid}", response_model=list[MatchScoreOut])
async def get_recommendations(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = current_user.get("role")
    if role != "candidate":
        raise HTTPException(
            status_code=403,
            detail="Access restricted: only candidates can upload resumes."
        )
    
    try:
        uid=current_user.get("uid", "N/A")
        results = await recommend_jobs(uid, db)
        print(results)
        return [{"job_id": job_id, "score": score} for job_id, score in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

