from typing import Annotated, Sequence

from fastapi import APIRouter, Request, Depends, status, Form, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserNotExists
from starlette.responses import RedirectResponse

from src.auth.models import User
from src.category import Category
from src.auth.fastapi_users import auth_backend_cookie, current_active_user_ui
from src.auth.manager import UserManager
from src.auth.dependencies import get_user_manager
from src.config import settings
from src.common.dependencies import get_categories
from src.common.csrf import generate_csrf_token, validate_csrf_token


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_auth, include_in_schema=False)


@router.get("/login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user:
        return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

    csrf_token_value = generate_csrf_token(request)

    response = templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "categories": categories,
            "user": user,
            "csrf_token_value": csrf_token_value,
        },
    )
    response.set_cookie(
        key=settings.csrf.token_name,
        value=csrf_token_value,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/logout", response_class=RedirectResponse)
async def logout(
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    user: Annotated[User, Depends(current_active_user_ui)],
):
    strategy = auth_backend_cookie.get_strategy()
    token = await strategy.read_token(request, user_manager=user_manager)
    if token:
        auth_backend_cookie.logout(strategy=strategy, user=user, token=token)
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key=auth_backend_cookie.transport.cookie_name,
        path=auth_backend_cookie.transport.cookie_path,
        domain=auth_backend_cookie.transport.cookie_domain,
        secure=auth_backend_cookie.transport.cookie_secure,
        httponly=auth_backend_cookie.transport.cookie_httponly,
        samesite=auth_backend_cookie.transport.cookie_samesite,
    )
    return response


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    csrf_token_cookie: str = Cookie(None, alias=settings.csrf.token_name),
    categories: Sequence[Category] = Depends(get_categories),
):
    if (
        not csrf_token_cookie
        or not validate_csrf_token(request, csrf_token_cookie)
        or csrf_token != csrf_token_cookie
    ):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Недействительный CSRF-токен",
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = await user_manager.authenticate(
            credentials=OAuth2PasswordRequestForm(
                username=email,
                password=password,
                scope="",
            )
        )
        if user is None:
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Неверный email или пароль",
                    "categories": categories,
                    "csrf_token_value": csrf_token,
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    except (InvalidPasswordException, UserNotExists):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Неверный email или пароль",
                "categories": categories,
                "csrf_token_value": csrf_token,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    strategy = auth_backend_cookie.get_strategy()
    token = await strategy.write_token(user)

    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=auth_backend_cookie.transport.cookie_name,
        value=token,
        max_age=auth_backend_cookie.transport.cookie_max_age,
        expires=auth_backend_cookie.transport.cookie_max_age,
        path=auth_backend_cookie.transport.cookie_path,
        domain=auth_backend_cookie.transport.cookie_domain,
        secure=auth_backend_cookie.transport.cookie_secure,
        httponly=auth_backend_cookie.transport.cookie_httponly,
        samesite=auth_backend_cookie.transport.cookie_samesite,
    )
    response.delete_cookie(
        key=settings.csrf.token_name,
        path="/",
    )
    return response
