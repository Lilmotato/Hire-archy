# app/main.py

import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import upload, users
from routers.auth import router as auth_router
from config.settings import settings
from db.database import Base, engine  # Your Async SQLAlchemy setup for Postgres
from db.mongo import ping_db  # MongoDB connection checker
from utils.logger import setup_logger


# Initialize logger
logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and Shutdown events."""
    
    # Create upload directory if it doesn't exist
    UPLOAD_DIRECTORY = "uploaded_resumes"
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Connect to Postgres (create tables)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ PostgreSQL tables created.")

    # Connect to MongoDB (ping)
    await ping_db()

    logger.info("🚀 Hire-archy backend started successfully.")
    yield
    logger.info("🛑 Hire-archy backend is shutting down.")

# Initialize FastAPI app
app = FastAPI(
    title="Hire-archy",
    version="1.0.0",
    lifespan=lifespan
)

# Include Routers
app.include_router(auth_router)
app.include_router(users.router)
app.include_router(upload.router, tags=["Resume Upload"])

# Public Endpoints
@app.get("/", tags=["Public"])
async def read_root():
    """Root public endpoint."""
    return {"message": "Hire-archy Backend API is running."}

@app.get("/healthz", tags=["Public"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "ok"}

