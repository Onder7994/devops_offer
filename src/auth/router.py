from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from src.auth.models import User
from src.auth.dependencies import get_user_manager
from src.auth.schemas import UserCreate, UserRead, UserUpdate
from src.config import settings

router = APIRouter()

bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.access_token.secret, lifetime_seconds=settings.access_token.lifetime_seconds,)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=settings.api.prefix_jwt,
    tags=["Auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=settings.api.prefix_auth,
    tags=["Auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix=settings.api.prefix_users,
    tags=["Users"],
)