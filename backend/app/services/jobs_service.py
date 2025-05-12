import asyncio
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import update
from schemas.jobs import JobListing
from db.mongo import get_mongo_client
from utils.dial_parser import get_text_embedding
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import setup_logger
from uuid import UUID

logger = setup_logger(__name__)
executor = ThreadPoolExecutor(max_workers=3)

async def store_job_summary_embedding(job_id: UUID, summary_text: str, db: AsyncSession):
    """
    Stores a job summary and its embedding into both MongoDB and PostgreSQL.

    Args:
        job_id (UUID): Unique identifier of the job listing.
        summary_text (str): Job summary text.
        db (AsyncSession): Async SQLAlchemy session for PostgreSQL.
    """
    try:
        loop = asyncio.get_running_loop()

        # Generate embedding in a non-blocking way
        embedding = await loop.run_in_executor(executor, get_text_embedding, summary_text)

        if not isinstance(embedding, list) or not all(isinstance(i, float) for i in embedding):
            raise ValueError(f"Invalid embedding output received: {embedding}")

        # Store summary and embedding in MongoDB
        await _update_mongo_summary(job_id, summary_text, embedding)

        # Store summary and embedding in PostgreSQL (PGVector)
        await db.execute(
            update(JobListing)
            .where(JobListing.id == job_id)
            .values(
                job_summary=summary_text.strip(),
                embedding=embedding
            )
        )
        await db.commit()
        logger.info(f"Job embedding successfully stored in PostgreSQL for job_id: {job_id}")

    except Exception as e:
        logger.error(f"Failed to store embedding for job_id {job_id}: {e}", exc_info=True)


async def _update_mongo_summary(job_id: UUID, summary_text: str, embedding: list[float]):
    """
    Updates MongoDB with the job summary and its embedding.

    Args:
        job_id (UUID): Job identifier.
        summary_text (str): Summary text.
        embedding (list[float]): Generated embedding.
    """
    mongo = get_mongo_client()
    db = mongo["mydb"]
    job_summaries = db["job_summaries"]

    result = await job_summaries.update_one(
        {"job_id": str(job_id)},
        {
            "$set": {
                "summary_text": summary_text.strip(),
                "embedding_vector": embedding
            }
        },
        upsert=True
    )

    if result.upserted_id:
        logger.info(f"Inserted new summary into MongoDB for job_id: {job_id}")
    else:
        logger.info(f"Updated existing summary in MongoDB for job_id: {job_id}")
