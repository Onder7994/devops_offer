from typing import Optional
import logging
from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.auth.models import User
from src.config import settings

logger = logging.getLogger(__name__)

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.access_token.secret
    verification_token_secret = settings.access_token.secret

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        logger.info("Пользователь %s успешно зарегистрирован.", user.email)