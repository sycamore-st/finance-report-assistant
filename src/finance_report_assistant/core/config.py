from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    sec_user_agent: str = Field(
        default="FinanceReportAssistant/0.1 (contact@example.com)",
        description="SEC-compliant user agent with contact info",
    )
    data_dir: Path = Field(default=Path("data"))


settings = Settings()
