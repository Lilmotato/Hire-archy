# app/routers/auth.py
from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Header, Request, status
from httpx import request
from db.database import get_db
from models.auth import LoginSchema, SignUpSchema, UserSignupResponse
from services.firebase_service import signup_candidate_service, login_service
from sqlalchemy.ext.asyncio import AsyncSession
from firebase_admin import auth


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


@router.post("/verify-token")
async def verify_token(token: str = Body(..., embed=True)):
    try:
        decoded_token = auth.verify_id_token(token)
        return {
            "valid": True,
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "role": decoded_token.get("role"),
            "decoded_token": decoded_token
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )