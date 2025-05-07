# app/main.py

import os
from sqlalchemy import text
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import upload, users, jobs
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

    # Connect to Postgres
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        # Create tables after the extension
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL tables and pgvector extension ready.")

    # Connect to MongoDB (ping)
    await ping_db()

    logger.info("Hire-archy backend started successfully.")
    yield
    logger.info("Hire-archy backend is shutting down.")

# Initialize FastAPI app
app = FastAPI(
    title="Hire-archy",
    version="1.0.0",
    lifespan=lifespan
)

# Allow origins (update with your actual frontend URL)
origins = [
    "http://localhost:3000",  # Next.js dev server
    "https://your-frontend-domain.com",  # Add production URL when needed
]

from fastapi.middleware.cors import CORSMiddleware
# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include Routers
app.include_router(auth_router)
app.include_router(users.router)
app.include_router(upload.router, tags=["Resume Upload"])
app.include_router(jobs.router, tags = ["Jobs"])

# Public Endpoints
@app.get("/", tags=["Public"])
async def read_root():
    """Root public endpoint."""
    return {"message": "Hire-archy Backend API is running."}

@app.get("/healthz", tags=["Public"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "ok"}

