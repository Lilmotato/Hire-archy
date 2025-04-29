# routers/upload_router.py
from sqlalchemy.future import select
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from requests import Session
from config.firebase import get_current_user  # <-- Important: use the same
from firebase_admin import auth
import boto3
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from schemas.user import User

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


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)  # ✅ AsyncSession
):
    # print("Current user UID:", current_user.uid)

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

    # ✅ Update user's resume_url asynchronously
    result = await db.execute(select(User).where(User.uid == uid))
    user = result.scalars().first()

    if user:
        user.resume_url = file_url
        await db.commit()
        await db.refresh(user)
    else:
        raise HTTPException(status_code=404, detail="User not found.")

    return {"message": "Resume uploaded successfully!", "file_url": file_url}


from db.mongo import database

router = APIRouter()

@router.get("/test")
async def test_mongo():
    users_collection = database.get_collection("users")

    # Mongo's new async operations
    user = await users_collection.find_one({"name": "John Doe"})
    
    return {"user": user}