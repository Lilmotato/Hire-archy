
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.models import User, JobListing
from app.db.session import get_db  # Adjust if different
import asyncio
import logging

mongo = AsyncIOMotorClient("mongodb://localhost:27017")
user_summaries = mongo["mydb"]["user_summaries"]
job_summaries = mongo["mydb"]["job_summaries"]

async def migrate_user_embeddings(db: AsyncSession):
    async for doc in user_summaries.find({}):
        uid = doc.get("user_id")
        vector = doc.get("embedding_vector")
        if not uid or not vector:
            continue

        result = await db.execute(select(User).where(User.uid == uid))
        user = result.scalar_one_or_none()
        if user:
            await db.execute(
                update(User).where(User.uid == uid).values(embedding=vector)
            )
            await db.commit()

async def migrate_job_embeddings(db: AsyncSession):
    async for doc in job_summaries.find({}):
        title = doc.get("title")
        company = doc.get("company_name")
        vector = doc.get("embedding_vector")
        if not title or not company or not vector:
            continue

        result = await db.execute(
            select(JobListing).where(
                JobListing.title == title,
                JobListing.company_name == company
            )
        )
        job = result.scalar_one_or_none()
        if job:
            await db.execute(
                update(JobListing)
                .where(JobListing.id == job.id)
                .values(embedding=vector)
            )
            await db.commit()

async def run_migration():
    async with get_db() as db:
        await migrate_user_embeddings(db)
        await migrate_job_embeddings(db)

if __name__ == "__main__":
    asyncio.run(run_migration())
