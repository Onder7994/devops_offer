from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
)

from src.config import settings
from src.auth.models import User
from src.auth.dependencies import get_user_manager


bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.access_token.secret,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(fastapi_users.current_user(active=True))]
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Allowed for admins only.",
        )
    return current_user
