import numpy as np
from numpy.linalg import norm
from sqlalchemy import select
from schemas.jobs import JobListing
from schemas.user import User
from db.match_score import get_existing_scores, upsert_score
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def cosine_sim(a, b):
    return float(np.dot(a, b) / (norm(a) * norm(b)))

async def recommend_jobs(uid: str, db):
    logger.info(f"Starting job recommendation for user UID: {uid}")

    result = await db.execute(select(User.embedding).where(User.uid == uid))
    user_emb = result.scalar_one_or_none()

    if user_emb is None:
        logger.warning("No embedding found for user.")
        return []

    logger.info("User embedding fetched successfully.")

    jobs_result = await db.execute(
        select(JobListing.id, JobListing.embedding).where(JobListing.embedding != None)
    )
    jobs = jobs_result.fetchall()

    logger.info(f"Total jobs fetched from database: {len(jobs)}")

    existing_scores = await get_existing_scores(uid, db)
    logger.info(f"Existing match scores retrieved: {len(existing_scores)}")

    results = []

    for job_id, job_emb in jobs:
        if str(job_id) in existing_scores:
            logger.info(f"Reusing existing score for job ID: {job_id}")
            results.append((job_id, existing_scores[str(job_id)]))
        else:
            logger.info(f"Computing new score for job ID: {job_id}")
            score = await cosine_sim(user_emb, job_emb)
            await upsert_score(db, uid, job_id, score)
            logger.info(f"New score computed and stored: {score:.4f}")
            results.append((job_id, score))

    results.sort(key=lambda x: x[1], reverse=True)
    logger.info("Job recommendation process completed.")
    return results[:10]
