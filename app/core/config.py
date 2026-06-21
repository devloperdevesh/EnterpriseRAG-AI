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

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://enterpriserag-ai.vercel.app",
    ]

    class Config:
        env_file = ".env"

settings = Settings()
