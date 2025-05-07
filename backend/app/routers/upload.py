# routers/upload_router.py
from grpc import Status
from sqlalchemy.future import select
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends, HTTPException
from requests import Session
from schemas.user import User
from config.firebase import get_current_user  # <-- Important: use the same
from firebase_admin import auth
import boto3
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.resume_service import save_parsed_resume_to_mongo
from utils.file_reader import extract_text
from utils.dial_parser import parse_resume_with_dial

router = APIRouter()

# Setup S3
BUCKET_NAME = "my-resume-bucket"
s3 = boto3.client(
    's3',
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

# Helper to create bucket if missing
def create_bucket_if_not_exists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except s3.exceptions.ClientError:
        s3.create_bucket(Bucket=bucket_name)

create_bucket_if_not_exists(BUCKET_NAME)

# Helper to generate unique filename
def generate_unique_filename(original_filename: str, user_uid: str) -> str:
    ext = original_filename.split('.')[-1]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{user_uid}-resume-{timestamp}-{unique_id}.{ext}"


from fastapi import BackgroundTasks

@router.post("/resume")
async def upload_resume(
    background_tasks: BackgroundTasks,  # Remember : In python Non-default argument (& required) follows default argument
    file: UploadFile = File(...),        # ✅ default after
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
     # 🔒 Check if user is a candidate
    role = current_user.get("role")
    if role != "candidate":
        raise HTTPException(
            status_code=403,
            detail="Access restricted: only candidates can upload resumes."
        )
    
    allowed_mimes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    uid = current_user.get("uid")

    unique_filename = generate_unique_filename(file.filename, user_uid=uid)
    file_content = await file.read()

    # Upload to S3
    s3_key = f"resumes/{unique_filename}"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=file_content,
        ContentType=file.content_type
    )

    file_url = f"http://localhost:4566/{BUCKET_NAME}/{s3_key}"

    # Update user's resume_url
    result = await db.execute(select(User).where(User.uid == uid))
    user = result.scalars().first()

    if user:
        user.resume_url = file_url
        try:
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error while updating resume URL.")
    else:
        raise HTTPException(status_code=404, detail="User not found.")

    # Background task
    background_tasks.add_task(
        process_resume_background_task,
        file_content,
        file.content_type,
        uid
    )

    return {"message": "Resume uploaded successfully!", "file_url": file_url}


async def process_resume_background_task(file_content: bytes, content_type: str, user_id: str):
    """Extract text, parse via LLM, and save parsed JSON into Mongo."""
    # 1. Extract plain text
    text = await extract_text(file_content, content_type)

    # 2. Parse with DIAL LLM
    parsed_resume = await parse_resume_with_dial(text)

    # 3. Save parsed JSON into MongoDB
    await save_parsed_resume_to_mongo(user_id, parsed_resume)