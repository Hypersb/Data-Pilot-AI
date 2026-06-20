from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:8501,http://localhost:8000,http://localhost:3000"
    session_ttl_seconds: int = 7200
    max_upload_mb: int = 25
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: float = 120.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
