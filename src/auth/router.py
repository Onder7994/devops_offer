from fastapi import APIRouter
from src.auth.fastapi_users import fastapi_users, auth_backend_bearer
from src.auth.schemas import UserCreate, UserRead, UserUpdate
from src.config import settings

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend_bearer),
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
