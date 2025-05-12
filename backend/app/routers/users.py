from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import json
from db.mongo import get_mongo_client
from utils.dial_parser import get_text_embedding
from db.database import get_db
from models.user import UserUpdateSchema
from schemas.user import User 
from config.firebase import get_current_user
from models.auth import UserInfo  
from utils.logger import setup_logger

router = APIRouter(prefix="/users", tags=["Users"])
logger = setup_logger(__name__)  


@router.get("/me", response_model=UserInfo)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    logger.info(f"👤 Fetching current user info for UID: {current_user.get('uid')}")
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
            f"Location: {user.location or 'N/A'}\n"
            f"Years of Experience: {user.years_of_experience or 'N/A'}\n"
            f"Key Skills: {', '.join(user.key_skills or [])}"
        )

        logger.debug(f"📝 Summary text for embedding:\n{summary_text}")

        embedding_vector = get_text_embedding(summary_text)
        logger.info(f"🧠 Embedding generated for UID: {user.uid}")

        await db.execute(
            update(User)
            .where(User.uid == user.uid)
            .values(embedding=embedding_vector)
        )
        await db.commit()
        logger.info(f"Embedding stored successfully for UID: {user.uid}")
    except Exception as e:
        logger.error(f"Embedding save failed for UID {user.uid}: {e}")
        raise


@router.put("/me", response_model=UserUpdateSchema)
async def update_my_profile(
    update_data: UserUpdateSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        uid = current_user['uid']
        logger.info(f"Updating profile for UID: {uid}")

        result = await db.execute(select(User).where(User.uid == uid))
        user = result.scalars().first()
        if not user:
            logger.warning(f"User not found: {uid}")
            raise HTTPException(status_code=404, detail="User not found.")

        # Get parsed resume from MongoDB
        # Get parsed resume from MongoDB
        mongo = get_mongo_client()
        parsed_resume = {}

        parsed_doc = await mongo["mydb"]["Candidates"].find_one({"uid": user.uid})
        if parsed_doc and isinstance(parsed_doc.get("parsed_resume"), dict):
            parsed_resume = parsed_doc["parsed_resume"]
        else:
            logger.warning(f"No valid parsed_resume found in MongoDB for UID: {user.uid}")

        # Fallback-safe updates
        user.full_name = update_data.full_name or parsed_resume.get("Name") or user.full_name
        user.phone_number = update_data.phone_number or parsed_resume.get("Phone Number") or user.phone_number
        user.location = update_data.location or parsed_resume.get("Location") or user.location
        user.years_of_experience = update_data.years_of_experience or parsed_resume.get("Years of Experience") or user.years_of_experience

        if update_data.key_skills:
            user.key_skills = update_data.key_skills
            logger.debug(f"Using provided key skills for UID: {uid}")
        elif "Skills" in parsed_resume:
            user.key_skills = parsed_resume["Skills"]
            logger.debug(f"Fallback to parsed skills for UID: {uid}")

        # ✅ Check if all fields are now complete
        if (
            user.full_name and
            user.phone_number and
            user.location and
            user.key_skills and isinstance(user.key_skills, list) and len(user.key_skills) > 0 and
            user.years_of_experience is not None
        ):
            user.profile_completed = True
            logger.info(f"Profile auto-marked complete for UID: {uid}")
        else:
            user.profile_completed = False
            logger.info(f"Profile still incomplete for UID: {uid}")

        await db.commit()
        await db.refresh(user)
        logger.info(f"Profile updated for UID: {user.uid}")

        background_tasks.add_task(generate_and_store_summary, user, db)
        logger.info(f"Background embedding task scheduled for UID: {user.uid}")
        return update_data

    except Exception as e:
        logger.exception(f"Update failed for UID: {current_user['uid']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
