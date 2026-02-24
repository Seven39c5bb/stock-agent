from typing import List

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    llm_base_url: str = "https://api.chatanywhere.tech"
    llm_api_key: str = ""
    llm_model: str = "gemini-3-flash-preview"
    llm_temperature: float = 0.2
    llm_timeout: int = 30
    debug: bool = False
    tushare_token: str = ""

    http_proxy: str = ""
    https_proxy: str = ""
    no_proxy: str = ""
    akshare_use_proxy: bool = False

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
