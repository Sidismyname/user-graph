from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()
