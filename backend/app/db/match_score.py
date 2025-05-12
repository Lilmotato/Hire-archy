from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.match_score import MatchScore
import uuid

async def get_existing_scores(uid: str, db: AsyncSession):
    stmt = select(MatchScore.job_id, MatchScore.score).where(MatchScore.uid == uid)
    result = await db.execute(stmt)
    return {str(row.job_id): row.score for row in result.fetchall()}

async def upsert_score(db: AsyncSession, uid: str, job_id, score: float):
    record = MatchScore(
        id=uuid.uuid4(),
        uid=uid,
        job_id=job_id,
        score=score
    )
    await db.merge(record)
    await db.commit()

async def get_top_jobs(uid: str, db: AsyncSession, limit: int = 10):
    stmt = (
        select(MatchScore.job_id, MatchScore.score)
        .where(MatchScore.uid == uid)
        .order_by(MatchScore.score.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()
