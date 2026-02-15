import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "replace-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dfc_tracking.db")

    class Config:
        env_file = ".env"


settings = Settings()
