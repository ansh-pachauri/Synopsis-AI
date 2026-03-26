from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    GEMINI_API_KEY: str
    TAVILY_API_KEY: str
    DATABASE_URL:str

@lru_cache
def settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
