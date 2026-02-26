from typing import List, Optional

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

    llm_analysis_base_url: str = ""
    llm_analysis_api_key: str = ""
    llm_analysis_model: str = ""
    llm_analysis_temperature: Optional[float] = None
    llm_analysis_timeout: Optional[int] = None

    llm_search_base_url: str = ""
    llm_search_api_key: str = ""
    llm_search_model: str = ""
    llm_search_temperature: Optional[float] = None
    llm_search_timeout: Optional[int] = None
    debug: bool = False
    tushare_token: str = ""

    http_proxy: str = ""
    https_proxy: str = ""
    no_proxy: str = ""
    akshare_use_proxy: bool = False

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def analysis_llm_base_url(self) -> str:
        return self.llm_analysis_base_url.strip() or self.llm_base_url

    @property
    def analysis_llm_api_key(self) -> str:
        return self.llm_analysis_api_key.strip() or self.llm_api_key

    @property
    def analysis_llm_model(self) -> str:
        return self.llm_analysis_model.strip() or self.llm_model

    @property
    def analysis_llm_temperature(self) -> float:
        return self.llm_analysis_temperature if self.llm_analysis_temperature is not None else self.llm_temperature

    @property
    def analysis_llm_timeout(self) -> int:
        return self.llm_analysis_timeout if self.llm_analysis_timeout is not None else self.llm_timeout

    @property
    def search_llm_base_url(self) -> str:
        return self.llm_search_base_url.strip() or self.llm_base_url

    @property
    def search_llm_api_key(self) -> str:
        return self.llm_search_api_key.strip() or self.llm_api_key

    @property
    def search_llm_model(self) -> str:
        return self.llm_search_model.strip() or self.llm_model

    @property
    def search_llm_temperature(self) -> float:
        return self.llm_search_temperature if self.llm_search_temperature is not None else self.llm_temperature

    @property
    def search_llm_timeout(self) -> int:
        return self.llm_search_timeout if self.llm_search_timeout is not None else self.llm_timeout


settings = Settings()
