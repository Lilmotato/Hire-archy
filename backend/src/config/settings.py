# app/config/settings.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FIREBASE_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
