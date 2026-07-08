from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "EnterpriseRAG"
    ENV: str = "production"

    # Security
    SECRET_KEY: str = "my_enterprise_rag_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Database 
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/enterprise_rag"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
