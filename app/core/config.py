from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Essay AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        

settings = Settings()