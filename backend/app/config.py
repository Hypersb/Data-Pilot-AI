from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8501"
    session_ttl_seconds: int = 7200
    max_upload_mb: int = 25
    llm_provider: str = "none"
    ollama_enabled: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: float = 30.0
    ollama_connect_timeout: float = 5.0
    rate_limit_enabled: bool = False
    rate_limit_uploads_per_minute: int = 10
    samples_dir: str | None = None

    def resolved_llm_provider(self) -> str:
        provider = self.llm_provider.strip().lower()
        if provider != "none":
            return provider
        return "ollama" if self.ollama_enabled else "none"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def resolved_samples_dir(self) -> Path:
        if self.samples_dir:
            return Path(self.samples_dir)
        return Path(__file__).resolve().parent.parent.parent / "sample-data"


settings = Settings()
