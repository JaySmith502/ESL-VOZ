from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///./eslvoice_dev.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    magic_link_expire_hours: int = 24 * 7  # 7 days
    resend_api_key: str | None = None
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"

    # AI vendors (all optional for M1; missing keys enable deterministic fallback)
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    deepgram_api_key: str | None = None

    # Email
    resend_api_key: str | None = None
    resend_from_email: str = "noreply@example.com"


settings = Settings()
