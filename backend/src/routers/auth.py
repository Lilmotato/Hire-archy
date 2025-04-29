# app/routers/auth.py
from fastapi import APIRouter, Body, Depends, HTTPException, status
from db.database import get_db
from models.auth import LoginSchema, SignUpSchema, UserSignupResponse
from services.firebase_service import signup_candidate_service, login_service
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup/candidate", response_model=UserSignupResponse)
async def signup_candidate(
    user_data: SignUpSchema = Body(...),
    db: AsyncSession = Depends(get_db)  # Inject db here!
):
    return await signup_candidate_service(user_data, db)


@router.post("/login", response_model=dict)
async def login(user_data: LoginSchema = Body(...)):
    return await login_service(user_data)
