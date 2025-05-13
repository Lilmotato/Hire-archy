# app/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Firebase
    firebase_api_key: str

    # MongoDB
    mongodb_uri: str

    # DIAL (LLM Parsing API)
    dialapi: str
    dial_deployment_name: str = "gpt-4" 
    dial_api_version: str = "2023-12-01-preview" 

    #postgres
    database_url: str

    class Config:
        env_file = ".env"  # Load variables from .env file

# Singleton instance
settings = Settings()
