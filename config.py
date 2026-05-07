from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        # Абсолютный путь к .env в папке проекта
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = "utf-8"

settings = Settings()
print(f"🔍 Загружена DATABASE_URL: {settings.DATABASE_URL}")