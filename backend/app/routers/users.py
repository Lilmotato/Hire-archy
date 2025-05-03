from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.database import get_db
from models.user import UserUpdateSchema, UserProfileResponse  # Pydantic schemas from models
from schemas.user import User  # ORM model (SQLAlchemy) from schemas
from config.firebase import get_current_user
from models.auth import UserInfo  # Assuming this is your current user response Pydantic model

router = APIRouter(prefix="/users", tags=["Users"])


router = APIRouter(prefix="/users", tags=["Users"])

# 🚀 Get current logged-in user details
@router.get("/me", response_model=UserInfo)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserInfo(
        uid=current_user.get("uid", "N/A"),
        email=current_user.get("email"),
        role=current_user.get("role"),
        email_verified=current_user.get("email_verified")
    )

# 🚀 Update profile (full_name, phone_number only)
@router.put("/me", response_model=UserUpdateSchema)
async def update_my_profile(
    update_data: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Fetch the user by UID
        result = await db.execute(select(User).where(User.uid == current_user["uid"]))
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # ✅ corrected here
                detail="User not found."
            )

        # Update only provided fields
        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        if update_data.phone_number is not None:
            user.phone_number = update_data.phone_number
        #location, yoe, key-skills

        await db.commit()
        await db.refresh(user)

        return update_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  # ✅ corrected here
            detail=f"Failed to update profile: {str(e)}"
        )
