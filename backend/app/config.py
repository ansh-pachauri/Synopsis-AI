from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    GEMINI_API_KEY: None | str
    TAVILY_API_KEY: str
    DATABASE_URL:str
    SUPABASE_URL:str
    SUPABASE_JWT_SECRET:str
    SUPABASE_ANON_KEY:str

@lru_cache
def settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
