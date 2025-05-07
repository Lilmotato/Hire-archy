# app/db/mongo.py

import os
from dotenv import load_dotenv
from pymongo import server_api
from pymongo import AsyncMongoClient

from utils.logger import setup_logger  # <<< your utils/logger.py
logger = setup_logger()

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

# Create the AsyncMongoClient instance
mongo_client: AsyncMongoClient = AsyncMongoClient(
    MONGODB_URI,
    server_api=server_api.ServerApi(version="1", strict=True, deprecation_errors=True)
)

async def ping_db():
    """Ping MongoDB on startup to verify connection."""
    try:
        await mongo_client.admin.command("ping")
        logger.info("MongoDB connection successful.")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")

def get_mongo_client() -> AsyncMongoClient:
    """Returns the MongoDB client instance for dependency injection."""
    return mongo_client
