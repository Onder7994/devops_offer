from typing import Annotated, Sequence

from fastapi import APIRouter, Request, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserNotExists, UserAlreadyExists
from starlette.responses import RedirectResponse

# from auth.fastapi_users import fastapi_users
from src.auth.schemas import UserCreate
from src.category import Category
from src.auth.fastapi_users import auth_backend_cookie
from src.auth.manager import UserManager
from src.auth.dependencies import get_user_manager
from src.config import settings
from src.common.dependencies import get_categories

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_auth, include_in_schema=False)


@router.get("/login", response_class=HTMLResponse, response_model=None)
async def login_form(
    request: Request,
    categories: Sequence[Category] = Depends(get_categories),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "categories": categories,
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    form_data = await request.form()
    email = form_data.get("username")
    password = form_data.get("password")

    try:
        user = await user_manager.authenticate(
            credentials=OAuth2PasswordRequestForm(
                username=email,
                password=password,
                scope="",
            )
        )
    except (InvalidPasswordException, UserNotExists):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный email или пароль"},
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
    return response


@router.get("/register", response_class=HTMLResponse, response_model=None)
async def register_form(
    request: Request,
    categories: Sequence[Category] = Depends(get_categories),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "categories": categories,
        },
    )


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    categories: Sequence[Category] = Depends(get_categories),
):
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")
    password_confirm = form_data.get("password_confirm")

    if not email or not password or not password_confirm:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Все поля обязательны для заполнения",
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if password != password_confirm:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Пароли не совпадают",
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_create = UserCreate(email=email, password=password)
        user = await user_manager.create(user_create)
    except UserAlreadyExists:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Пользователь с таким email уже существует",
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except InvalidPasswordException as err:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": str(err),
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Произошла неизвестная ошибка. Пожалуйста, попробуйте позже",
                "categories": categories,
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
    return response
