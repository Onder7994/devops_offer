from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
    CookieTransport,
)

from src.config import settings
from src.auth.models import User
from src.auth.dependencies import get_user_manager


bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")

cookie_transport = CookieTransport(
    cookie_name="auth",
    cookie_max_age=settings.access_token.lifetime_seconds,
    cookie_secure=False,
    cookie_httponly=True,
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.access_token.secret,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )


auth_backend_bearer = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

auth_backend_cookie = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend_bearer],
)

fastapi_users_ui = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend_cookie],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_user_ui = fastapi_users_ui.current_user(active=True, optional=True)
current_active_superuser_ui = fastapi_users_ui.current_user(
    active=True, superuser=True, optional=True
)
