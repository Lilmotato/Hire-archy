from pydantic import BaseModel, EmailStr

class UserSignupResponse(BaseModel):
    uid: str
    email: EmailStr
    role: str
    message: str

class UserInfo(BaseModel):
    uid: str
    email: EmailStr | None = None 
    role: str | None = None # Role from custom claims
    email_verified: bool | None = None

class SignUpSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@gmail.com",
                "password": "securepassword123"
            }
        }

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@gmail.com",
                "password": "securepassword123"
            }
        }