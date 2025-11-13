"""Application configuration using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    APP_NAME: str = "Data Dictionary Generator"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = False
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./data/app.db"
    # Note: Database type is auto-detected from DATABASE_URL using is_sqlite/is_postgresql properties

    # PostgreSQL-specific settings (ignored for SQLite)
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # SQLite-specific settings
    SQLITE_TIMEOUT: int = 30
    SQLITE_CHECK_SAME_THREAD: bool = False

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6380/0"
    REDIS_CACHE_TTL: int = 3600

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    API_KEY_ENABLED: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]

    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_ENABLED: bool = True

    # File Processing
    MAX_FILE_SIZE_MB: int = 500
    MAX_RECORDS_TO_ANALYZE: int = 10000
    SAMPLE_SIZE: int = 100
    STREAMING_CHUNK_SIZE: int = 65536

    # XML Processing
    XML_MAX_DEPTH: int = 10
    XML_STRIP_NAMESPACES: bool = True
    XML_ATTRIBUTE_PREFIX: str = "@"

    # Export Settings
    EXCEL_MAX_ROWS: int = 1048576
    EXPORT_TEMP_DIR: str = "/tmp/data-dict-exports"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60

    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    METRICS_ENABLED: bool = False

    # Email Notifications
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@datadictgen.com"

    # Background Jobs (Phase 2)
    CELERY_BROKER_URL: str = "redis://localhost:6380/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6380/2"

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.DATABASE_URL.lower()

    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return "postgresql" in self.DATABASE_URL.lower()

    @property
    def batch_commit_size(self) -> int:
        """Get optimal batch size for bulk operations based on database type."""
        return 100 if self.is_sqlite else 1000


# Global settings instance
settings = Settings()
