import hashlib
import logging
import secrets
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_reset_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(48)
    return token, hash_reset_token(token)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def deliver_reset_link(recipient: str, reset_url: str) -> None:
    if settings.SMTP_HOST and settings.SMTP_FROM_EMAIL:
        message = EmailMessage()
        message["Subject"] = "Reset your GLOBALCO EMS password"
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = recipient
        message.set_content(
            f"Use this link to reset your password. It expires in "
            f"{settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes:\n\n{reset_url}"
        )
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        return

    if settings.ENVIRONMENT.lower() == "development":
        logger.warning("Development password-reset URL: %s", reset_url)
