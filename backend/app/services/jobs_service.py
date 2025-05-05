import asyncio
from concurrent.futures import ThreadPoolExecutor
from db.mongo import get_mongo_client
from utils.dial_parser import get_text_embedding  # your sync embedding function

executor = ThreadPoolExecutor(max_workers=3)  # Avoid blocking event loop

async def store_job_summary_embedding(job_id, summary_text):
    try:
        loop = asyncio.get_running_loop()

        # ⛔ Avoid blocking event loop with big sync call
        embedding = await loop.run_in_executor(
            executor, get_text_embedding, summary_text
        )

        # ✅ Defensive: ensure embedding is a list of floats
        if not isinstance(embedding, list) or not all(isinstance(i, float) for i in embedding):
            raise ValueError(f"Invalid embedding output: {embedding}")

        # ✅ Keep Mongo ops fast and efficient
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
            print(f"✅ Inserted new summary for job {job_id}")
        else:
            print(f"✅ Updated summary for job {job_id}")

    except Exception as e:
        import logging
        logging.error(f"❌ Failed to store embedding for job {job_id}: {e}")
