from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "EnterpriseRAG"
    ENV: str = "production"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Database 
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
