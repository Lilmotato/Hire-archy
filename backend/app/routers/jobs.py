from sqlalchemy import select 
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

# Dependencies and utilities
from config.firebase import get_current_user  # 🔐 Auth middleware using Firebase
from schemas.jobs import JobListing  # 📦 SQLAlchemy model (Postgres table)
from services.jobs_service import store_job_summary_embedding  # 🧠 Background embedding task
from db.database import get_db  # 🔌 Async DB session for Postgres
from models.job import JobListingCreate, JobListingOut  # 📤 Pydantic request/response schemas
from utils.dial_parser import get_text_embedding  # 🤖 LLM summary/embedding utility
from db.mongo import get_mongo_client  # 🍃 MongoDB client

router = APIRouter()

# 🎯 POST endpoint to create a job listing
@router.post("/jobs", response_model=JobListingOut, status_code=status.HTTP_201_CREATED)
async def create_job_listing(
    job: JobListingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # ✅ Step 1: Ensure user is a recruiter (no fakers allowed)
    if current_user.get("role") != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can post jobs."
        )

    # ✅ Step 2: Create summary text to later embed using LLM
    summary_text = f"""
    Job Title: {job.title}
    Description: {job.description}
    Skills: {', '.join(job.key_skills)}
    Experience Required: {job.experience_required} years
    Location: {job.location}
    Company: {job.company_name}
    """

    # ✅ Step 3: Create the SQLAlchemy job object
    new_job = JobListing(
        id=uuid4(),
        title=job.title,
        description=job.description,
        key_skills=job.key_skills,
        experience_required=job.experience_required,
        location=job.location,
        company_name=job.company_name,
        recruiter_id=current_user["uid"],
        job_summary=summary_text.strip(),  # Cleaned up multi-line string
        is_active=True,
    )

    # ✅ Step 4: Save the job to PostgreSQL
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)  # 🔁 Get auto fields like created_at

    # ✅ Step 5: Background task for LLM embedding (non-blocking)
    background_tasks.add_task(store_job_summary_embedding, new_job.id, summary_text)

    # ✅ Step 6: Return clean response
    return new_job

# 🧼 GET all active jobs, optionally filter by location and skill
@router.get("/jobs/active", response_model=List[JobListingOut])
async def get_active_jobs_with_filters(
    location: Optional[str] = Query(None),  # 🔍 Optional filter by location
    skill: Optional[str] = Query(None),     # 🔍 Optional filter by skill
    db: AsyncSession = Depends(get_db),
):
    stmt = select(JobListing).where(JobListing.is_active == True)

    if location:
        stmt = stmt.where(JobListing.location.ilike(f"%{location}%"))  # Case-insensitive search

    if skill:
        stmt = stmt.where(JobListing.key_skills.any(skill))  # 🔎 Uses PostgreSQL ARRAY operator

    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return jobs

# 🧑‍💼 GET jobs posted by currently logged-in recruiter
@router.get("/jobs/recruiter", response_model=List[JobListingOut])
async def get_my_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 🛑 Only recruiters can access this
    if current_user["role"] != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view their jobs.")

    result = await db.execute(
        select(JobListing).where(JobListing.recruiter_id == current_user["uid"])
    )
    jobs = result.scalars().all()
    return jobs

# ⚠️ IMPORTANT: Static route above, dynamic below (avoid UUID parsing issues)
# 🧾 GET a specific job by ID
@router.get("/jobs/{job_id}", response_model=JobListingOut)
async def get_job_by_id(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(JobListing, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job
