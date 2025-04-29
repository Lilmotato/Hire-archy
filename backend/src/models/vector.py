from pydantic import BaseModel, Field

class VectorSchema(BaseModel):
    text: str
    deployment_name: str = Field(default="text-embedding-ada-002")
    api_version: str = Field(default="2023-12-01-preview")

