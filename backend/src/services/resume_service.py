# services/candidate_service.py

from utils.file_reader import extract_text
from utils.llm_parser import parse_resume_with_llm
from database.mongo import get_mongo_client

async def process_resume_upload(file_content: bytes, content_type: str, candidate_id: str):
    """Extract text, parse using LLM, and update candidate record."""
    
    # 1. Extract plain text
    text = await extract_text(file_content, content_type)

    # 2. Send to LLM
    parsed_resume = await parse_resume_with_llm(text)

    # 3. Save parsed JSON to MongoDB
    mongo_client = get_mongo_client()
    db = mongo_client["hierarchy-db"]
    candidates = db["candidates"]

    await candidates.update_one(
        {"_id": candidate_id},
        {"$set": {"parsed_resume": parsed_resume}}
    )
