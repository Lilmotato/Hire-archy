# app/services/firebase_service.py
import os
import requests
from firebase_admin import auth
from fastapi import Depends, HTTPException, status
from schemas.user import User
from db.database import get_db
from models.auth import SignUpSchema, UserSignupResponse, LoginSchema
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
import httpx



load_dotenv()

async def signup_candidate_service(
    user_data: SignUpSchema,
    db: AsyncSession   # <- No Depends here. Just a parameter
) -> UserSignupResponse:
    try:
        # Create Firebase user
        new_user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            email_verified=False,
            disabled=False
        )

        # Set Firebase custom claims
        auth.set_custom_user_claims(new_user.uid, {'role': 'candidate'})

        # Add new user to PostgreSQL
        user_record = User(
            uid=new_user.uid,
            email=new_user.email,
            role="candidate",
            full_name=None,
            phone_number=None,
            resume_url=None
        )

        db.add(user_record)
        await db.commit()       # ✅ use await because it's AsyncSession
        await db.refresh(user_record)

        return UserSignupResponse(
            uid=new_user.uid,
            email=new_user.email,
            role="candidate",
            message="User created successfully as a candidate."
        )

    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The email {user_data.email} is already registered."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during signup. {str(e)}"
        )


#login logic 
async def login_service(user_data: LoginSchema) -> dict:
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
    if not FIREBASE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server configuration error."
        )

    signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.post(signin_url, json={
            "email": user_data.email,
            "password": user_data.password,
            "returnSecureToken": True
        })

    print(response.json())
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials."
        )

    id_token = response.json()["idToken"]
    decoded_token = auth.verify_id_token(id_token)
    # role = decoded_token.get("role")

    # # if role != "candidate":
    # #     raise HTTPException(
    # #         status_code=status.HTTP_403_FORBIDDEN,
    # #         detail="User does not have candidate access."
    # #     )

    return {"token": id_token}

