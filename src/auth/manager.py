from typing import Optional
import logging
from fastapi import Request, HTTPException, status
from fastapi_users import BaseUserManager, IntegerIDMixin, models
from src.auth.models import User
from src.config import settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

logger = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.access_token.secret
    verification_token_secret = settings.access_token.secret

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        logger.info("Пользователь %s успешно зарегистрирован.", user.email)

    async def on_after_forgot_password(
        self, user: models.UP, token: str, request: Optional[Request] = None
    ) -> None:
        reset_url = f"{request.url.scheme}://{request.url.hostname}/auth/password-reset-confirm?token={token}"
        message = MessageSchema(
            subject="Сброс пароля",
            recipients=[user.email],
            body=f"Чтобы сбросить пароль, перейдите по ссылке: {reset_url}",
            subtype="plain",
        )
        fm_conf = ConnectionConfig(
            MAIL_USERNAME=settings.mail.username,
            MAIL_PASSWORD=settings.mail.password,
            MAIL_FROM=settings.mail.from_mail,
            MAIL_PORT=settings.mail.port,
            MAIL_SERVER=settings.mail.server,
            MAIL_STARTTLS=settings.mail.tls,
            MAIL_SSL_TLS=settings.mail.ssl,
            USE_CREDENTIALS=settings.mail.use_credentials,
            VALIDATE_CERTS=settings.mail.validate_certs,
            MAIL_FROM_NAME=settings.mail.from_mail_name,
        )
        fm = FastMail(fm_conf)
        try:
            await fm.send_message(message)
        except Exception as err:
            logger.error("Ошибка: %s", err)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
