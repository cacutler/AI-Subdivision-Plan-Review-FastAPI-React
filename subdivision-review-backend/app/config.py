from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Postgres — use asyncpg driver prefix for SQLAlchemy async
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/plansdb"
    db_echo: bool = False

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8 hours

    # File storage — local path in dev, swap for an S3 URL prefix in prod
    upload_dir: str = "/tmp/plans_uploads"
    max_upload_bytes: int = 50 * 1024 * 1024  # 50 MB

    # AI review
    anthropic_api_key: str = ""
    review_model: str = "claude-sonnet-4-6"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
