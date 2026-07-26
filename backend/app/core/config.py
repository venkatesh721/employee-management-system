from urllib.parse import urlparse

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    DATABASE_URL: str = "sqlite:///./ems.db"
    SECRET_KEY: str = "775c9ca579333f54cdd77cf44c5b515e"
    JWT_SECRET_KEY: str | None = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    OPENAI_API_KEY: str | None = None
    AI_MODEL: str = "gpt-4o-mini"
    ENABLE_EXTERNAL_AI: bool = False
    COMPANY_START_TIME: str = "09:00"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_USE_TLS: bool = True
    AUTH_RATE_LIMIT_REQUESTS: int = 10
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 60
    LOG_LEVEL: str = "INFO"
    DEFAULT_ADMIN_NAME: str = "Venkatesh"
    DEFAULT_ADMIN_USERNAME: str = "venkatesh"
    DEFAULT_ADMIN_EMAIL: str = "admin@example.com"
    DEFAULT_ADMIN_PASSWORD: str = "Admin@123"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value):
        """Render and older providers may expose the deprecated postgres:// scheme."""
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT.lower() != "production":
            return self

        if not self.DATABASE_URL.startswith("postgresql+psycopg://"):
            raise ValueError("Production requires a PostgreSQL DATABASE_URL")

        secret = self.JWT_SECRET_KEY or self.SECRET_KEY
        if len(secret) < 32 or secret in {
            "your-super-secret-key-change-in-production",
            "replace-with-at-least-32-random-characters",
        }:
            raise ValueError(
                "Production requires a unique secret of at least 32 characters"
            )

        origins = [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]
        if not origins:
            raise ValueError(
                "Production requires at least one exact CORS_ORIGINS value"
            )
        for origin in origins:
            parsed = urlparse(origin)
            if (
                parsed.scheme != "https"
                or not parsed.netloc
                or parsed.path not in ("", "/")
                or "*" in origin
                or parsed.hostname in {"localhost", "127.0.0.1"}
            ):
                raise ValueError(
                    "Production CORS_ORIGINS must contain exact HTTPS origins only"
                )

        frontend = urlparse(self.FRONTEND_URL)
        if (
            frontend.scheme != "https"
            or not frontend.netloc
            or frontend.path not in ("", "/")
            or frontend.hostname in {"localhost", "127.0.0.1"}
        ):
            raise ValueError("Production FRONTEND_URL must be an exact HTTPS origin")

        if not all(
            (
                self.SMTP_HOST,
                self.SMTP_USERNAME,
                self.SMTP_PASSWORD,
                self.SMTP_FROM_EMAIL,
            )
        ):
            raise ValueError(
                "Production requires SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, "
                "and SMTP_FROM_EMAIL"
            )
        if self.SMTP_PASSWORD == "your-google-app-password":
            raise ValueError(
                "Production SMTP_PASSWORD must be a real provider credential, "
                "not the example placeholder"
            )
        return self


settings = Settings()
