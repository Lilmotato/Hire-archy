from sqlalchemy import desc, select, update 
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

# Dependencies and utilities
from schemas.user import User
from schemas.match_score import MatchScore
from config.firebase import get_current_user  
from schemas.jobs import JobListing  
from services.jobs_service import store_job_summary_embedding 
from db.database import get_db  # Async DB session for Postgres
from models.job import JobListingCreate, JobListingOut  #  Pydantic request/response schemas
from utils.dial_parser import get_text_embedding  #  LLM summary/embedding utility
from db.mongo import get_mongo_client  
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

@router.post("/jobs", response_model=JobListingOut, status_code=status.HTTP_201_CREATED)
async def create_job_listing(
    job: JobListingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Ensure user is a recruiter
    if current_user.get("role") != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can post jobs."
        )

    # Create summary text
    summary_text = f"""
    Job Title: {job.title}
    Description: {job.description}
    Skills: {', '.join(job.key_skills)}
    Experience Required: {job.experience_required} years
    Location: {job.location}
    """

    # Create job entry
    new_job = JobListing(
        id=uuid4(),
        title=job.title,
        description=job.description,
        key_skills=job.key_skills,
        experience_required=job.experience_required,
        location=job.location,
        company_name=job.company_name,
        recruiter_id=current_user["uid"],
        job_summary=summary_text.strip(),
        is_active=True,
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Add background task with db
    background_tasks.add_task(store_job_summary_embedding, new_job.id, summary_text, db)

    return new_job

#  GET jobs posted by currently logged-in recruiter
@router.get("/jobs/recruiter", response_model=List[JobListingOut])
async def get_my_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    #  Only recruiters can access this
    if current_user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view their jobs.")

    result = await db.execute(
        select(JobListing).where(JobListing.recruiter_id == current_user["uid"])
    )
    jobs = result.scalars().all()
    return jobs

# IMPORTANT: Static route above, dynamic below (avoid UUID parsing issues)
# GET a specific job by ID
@router.get("/jobs/{job_id}", response_model=JobListingOut)
async def get_job_by_id(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(JobListing, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.post("/jobs/{job_id}/apply", status_code=status.HTTP_200_OK)
async def apply_to_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    uid = current_user["uid"]

    # Role-based access control
    if current_user["role"] != "candidate":
        logger.warning(f"Unauthorized apply attempt by user {uid} with role {current_user['role']}")
        raise HTTPException(status_code=403, detail="Only candidates can apply to jobs.")

    # Fetch job by ID
    result = await db.execute(select(JobListing).where(JobListing.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        logger.warning(f"Job with ID {job_id} not found.")
        raise HTTPException(status_code=404, detail="Job not found")

    if uid in job.applied_user_ids:
        logger.info(f"User {uid} has already applied to job {job_id}")
        raise HTTPException(status_code=400, detail="Already applied to this job")

    # Add UID to applied_user_ids
    updated_applied_ids = job.applied_user_ids + [uid]

    await db.execute(
        update(JobListing)
        .where(JobListing.id == job_id)
        .values(applied_user_ids=updated_applied_ids)
    )
    await db.commit()

    logger.info(f"User {uid} successfully applied to job {job_id}")
    return {"message": "Application successful"}

@router.get("/ranked-candidates")
async def rank_candidates(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Access Control
    if current_user["role"] != "recruiter":
        logger.warning(f"Unauthorized access attempt by user {current_user['uid']}")
        raise HTTPException(status_code=403, detail="Only recruiters can access candidate rankings.")

    # Step 1: Fetch job and validate recruiter ownership
    job_result = await db.execute(select(JobListing).where(JobListing.id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        logger.warning(f"Job with ID {job_id} not found.")
        raise HTTPException(status_code=404, detail="Job not found")

    if job.recruiter_id != current_user["uid"]:
        logger.warning(f"Recruiter {current_user['uid']} tried to access unauthorized job {job_id}")
        raise HTTPException(status_code=403, detail="Access denied. You do not own this job.")

    if not job.applied_user_ids:
        logger.info(f"No users have applied to job {job_id}")
        return {"candidates": []}

    # Step 2: Fetch match scores
    scores_result = await db.execute(
        select(MatchScore.uid, MatchScore.score)
        .where(
            MatchScore.job_id == job_id,
            MatchScore.uid.in_(job.applied_user_ids)
        )
        .order_by(desc(MatchScore.score))
    )
    score_data = scores_result.fetchall()

    if not score_data:
        logger.info(f"No match scores found for job {job_id}")
        return {"candidates": []}

    # Step 3: Fetch user details
    uids = [uid for uid, _ in score_data]
    users_result = await db.execute(
        select(User.uid, User.full_name, User.email, User.phone_number, User.resume_url,
               User.key_skills, User.location, User.years_of_experience)
        .where(User.uid.in_(uids))
    )
    users = {user.uid: user for user in users_result.fetchall()}

    # Step 4: Combine
    ranked_candidates = []
    for uid, score in score_data:
        user = users.get(uid)
        if user:
            ranked_candidates.append({
                "uid": uid,
                "score": round(score, 4),
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "resume_url": user.resume_url,
                "key_skills": user.key_skills,
                "location": user.location,
                "years_of_experience": user.years_of_experience,
            })

    logger.info(f"{len(ranked_candidates)} ranked candidates returned for job {job_id}")
    return {"candidates": ranked_candidates}