from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import json
from db.mongo import get_mongo_client
from utils.dial_parser import get_text_embedding
from db.database import get_db
from models.user import UserUpdateSchema
from schemas.user import User  # ORM model (SQLAlchemy) from schemas
from config.firebase import get_current_user
from models.auth import UserInfo  # Assuming this is your current user response Pydantic model
from utils.logger import setup_logger

  # ✅ Logging utility
router = APIRouter(prefix="/users", tags=["Users"])
logger = setup_logger(__name__)  # ✅ Named logger per module


# 🚀 Get current logged-in user details
@router.get("/me", response_model=UserInfo)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserInfo(
        uid=current_user.get("uid", "N/A"),
        email=current_user.get("email"),
        role=current_user.get("role"),
        email_verified=current_user.get("email_verified")
    )


async def generate_and_store_summary(user: User, db: AsyncSession):
    try:
        logger.info(f"📦 Starting summary generation for UID: {user.uid}")

        summary_text = (
            f"UID: {user.uid}\n"
            f"Location: {user.location or 'N/A'}\n"
            f"Years of Experience: {user.years_of_experience or 'N/A'}\n"
            f"Key Skills: {', '.join(user.key_skills or [])}"
        )

        logger.debug(f"📝 Summary:\n{summary_text}")

        embedding_vector = get_text_embedding(summary_text)
        logger.info(f"✅ Embedding generated for UID: {user.uid}")

        await db.execute(
            update(User)
            .where(User.uid == user.uid)
            .values(embedding=embedding_vector)
        )
        await db.commit()
        logger.info(f"📌 PostgreSQL update success for UID {user.uid}")
    except Exception as e:
        logger.error(f"❌ Embedding save failed for UID {user.uid}: {e}")
        raise


@router.put("/me", response_model=UserUpdateSchema)
async def update_my_profile(
    update_data: UserUpdateSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"🔄 Updating profile for UID: {current_user['uid']}")

        result = await db.execute(select(User).where(User.uid == current_user["uid"]))
        user = result.scalars().first()
        if not user:
            logger.warning(f"User not found: {current_user['uid']}")
            raise HTTPException(status_code=404, detail="User not found.")

        mongo = get_mongo_client()
        parsed_doc = await mongo["mydb"]["Candidates"].find_one({"uid": user.uid})
        raw_parsed = parsed_doc.get("parsed_resume", {}) if parsed_doc else {}
        parsed_resume = json.loads(raw_parsed) if isinstance(raw_parsed, str) else raw_parsed

        user.full_name = update_data.full_name or parsed_resume.get("full_name")
        user.phone_number = update_data.phone_number or parsed_resume.get("phone_number")
        user.location = update_data.location or parsed_resume.get("location")
        user.years_of_experience = update_data.years_of_experience or parsed_resume.get("years_of_experience")

        if update_data.key_skills:
            user.key_skills = update_data.key_skills
        elif "skills" in parsed_resume:
            user.key_skills = parsed_resume["skills"]

        await db.commit()
        await db.refresh(user)
        logger.info(f"✅ SQL profile updated for UID: {user.uid}")

        background_tasks.add_task(generate_and_store_summary, user)
        return update_data

    except Exception as e:
        logger.exception(f"❌ Update failed for UID: {current_user['uid']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
