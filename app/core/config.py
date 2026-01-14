from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Enterprise GenAI Backend"
    ENV: str = "development"

    # Security
    SECRET_KEY: str = "change-this-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Feature flags
    ENABLE_AUTH: bool = True
    ENABLE_COST_TRACKING: bool = True
    ENABLE_EVALUATION: bool = True

    class Config:
        env_file = ".env"


settings = Settings()