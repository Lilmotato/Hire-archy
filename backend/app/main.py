import os
from sqlalchemy import text
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import upload, users, jobs
from routers.auth import router as auth_router
from config.settings import settings
from db.database import Base, engine  
from db.mongo import ping_db  
from utils.logger import setup_logger
from routers import match_score
from routers import search




logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and Shutdown events."""    
    UPLOAD_DIRECTORY = "uploaded_resumes"
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL tables and pgvector extension ready.")
    
    await ping_db()

    logger.info("Hire-archy backend started successfully.")
    yield
    logger.info("Hire-archy backend is shutting down.")


app = FastAPI(
    title="Hire-archy",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",  
    "https://your-frontend-domain.com",  
]

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(auth_router)
app.include_router(users.router)
app.include_router(upload.router, tags=["Resume Upload"])
app.include_router(jobs.router, tags = ["Jobs"])
app.include_router(match_score.router)
app.include_router(search.router)

@app.get("/", tags=["Public"])
async def read_root():
    """Root public endpoint."""
    return {"message": "Hire-archy Backend API is running."}

@app.get("/healthz", tags=["Public"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "ok"}

