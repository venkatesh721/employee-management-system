import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_legacy_postgres_url_is_normalized():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgres://user:pass@db.example/globalco",
    )
    assert settings.DATABASE_URL == (
        "postgresql+psycopg://user:pass@db.example/globalco"
    )


def test_production_rejects_sqlite():
    with pytest.raises(ValidationError, match="Production requires a PostgreSQL"):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            DATABASE_URL="sqlite:///./ems.db",
        )


def production_settings(**overrides):
    values = {
        "DATABASE_URL": "postgresql://user:password@db.example.com/ems",
        "SECRET_KEY": "a-unique-production-secret-that-is-long-enough",
        "ENVIRONMENT": "production",
        "CORS_ORIGINS": "https://ems.example.com",
        "FRONTEND_URL": "https://ems.example.com",
        "SMTP_HOST": "smtp.example.com",
        "SMTP_USERNAME": "mailer",
        "SMTP_PASSWORD": "smtp-secret",
        "SMTP_FROM_EMAIL": "noreply@example.com",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def test_valid_production_settings_are_accepted():
    settings = production_settings()

    assert settings.DATABASE_URL.startswith("postgresql+psycopg://")


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"SECRET_KEY": "too-short"}, "unique secret"),
        ({"CORS_ORIGINS": "*"}, "exact HTTPS origins"),
        ({"CORS_ORIGINS": "http://localhost:3000"}, "exact HTTPS origins"),
        ({"FRONTEND_URL": "http://localhost:3000"}, "exact HTTPS origin"),
        ({"SMTP_PASSWORD": None}, "Production requires SMTP_HOST"),
    ],
)
def test_production_rejects_insecure_or_incomplete_settings(override, message):
    with pytest.raises(ValidationError, match=message):
        production_settings(**override)
