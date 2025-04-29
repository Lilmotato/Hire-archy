from pydantic import BaseModel, EmailStr

class UserSignupResponse(BaseModel):
    uid: str
    email: EmailStr
    role: str
    message: str

# Added for the /users/me endpoint
class UserInfo(BaseModel):
    uid: str
    email: EmailStr | None = None # Email might not always be present
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