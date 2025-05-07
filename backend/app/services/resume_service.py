import logging
from utils.file_reader import extract_text
from utils.dial_parser import parse_resume_with_dial
from db.mongo import get_mongo_client

logger = logging.getLogger(__name__)

async def process_resume_upload(file_content: bytes, content_type: str, candidate_id: str):
    """Extract text, parse using LLM, and update candidate record."""
    
    # 1. Extract plain text
    text = await extract_text(file_content, content_type)

    # 2. Send to LLM
    parsed_resume = await parse_resume_with_dial(text)  # ✅ Correct function

    # 3. Save parsed JSON to MongoDB
    mongo_client = get_mongo_client()
    db = mongo_client["mydb"]  
    candidates = db["Candidates"]

    await candidates.update_one(
        {"uid": candidate_id},
        {"$set": {"parsed_resume": parsed_resume}},
        upsert=True  # ✅ Upsert (important) so first-time users are created
    )


async def save_parsed_resume_to_mongo(user_id: str, parsed_resume: dict):
    """Save parsed resume JSON under user ID."""
    mongo_client = get_mongo_client()
    db = mongo_client["mydb"]  # ✅ your DB name
    candidates = db["Candidates"]  # ✅ your collection name

    try:
        result = await candidates.update_one(
            {"uid": user_id},
            {"$set": {"parsed_resume": parsed_resume}},
            upsert=True
        )
        if result.upserted_id:
            logger.info(f"✅ Inserted new document for user_id: {user_id}")
        else:
            logger.info(f"✅ Updated existing document for user_id: {user_id}")
    except Exception as e:
        logger.exception(f"❌ Failed to save parsed resume for user_id={user_id}")
        raise
