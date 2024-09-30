from typing import Annotated, Sequence

from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import (
    UserNotExists,
    UserAlreadyExists,
    InvalidResetPasswordToken,
)
from pydantic import ValidationError, EmailStr
from starlette.responses import RedirectResponse

from src.auth.schemas import RegisterForm

from src.auth.models import User
from src.auth.schemas import UserCreate
from src.category import Category
from src.auth.fastapi_users import auth_backend_cookie, current_active_user_ui
from src.auth.manager import UserManager
from src.auth.dependencies import get_user_manager
from src.config import settings
from src.common.dependencies import get_categories

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

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "categories": categories,
            "user": user,
        },
    )


@router.get("/password-reset", response_class=HTMLResponse)
async def reset_password_form(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user:
        return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "auth/password_reset.html",
        {
            "request": request,
            "categories": categories,
            "user": user,
        },
    )


@router.post("/password-reset", response_class=HTMLResponse)
async def password_reset(
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    categories: Sequence[Category] = Depends(get_categories),
    email: EmailStr = Form(...),
):
    try:
        user = await user_manager.get_by_email(user_email=email)

    except UserNotExists:
        return templates.TemplateResponse(
            "auth/password_reset.html",
            {
                "request": request,
                "error": "Пользователь не найден",
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await user_manager.forgot_password(user, request)
    return templates.TemplateResponse(
        "auth/password_reset.html",
        {
            "request": request,
            "message": "Инструкция по сбросу пароля отправлена на Вашу почту",
            "categories": categories,
        },
        status_code=status.HTTP_200_OK,
    )


@router.get("/password-reset-confirm", response_class=HTMLResponse)
async def password_reset_confirm(
    request: Request,
    token: str,
    categories: Sequence[Category] = Depends(get_categories),
):
    return templates.TemplateResponse(
        "auth/password_reset_confirm.html",
        {
            "request": request,
            "token": token,
            "categories": categories,
        },
    )


@router.post("/password-reset-confirm", response_class=HTMLResponse)
async def password_reset_confirm_post(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    user_manager: UserManager = Depends(get_user_manager),
    categories: Sequence[Category] = Depends(get_categories),
):
    try:
        user = await user_manager.reset_password(token, new_password, request)
    except InvalidResetPasswordToken:
        return templates.TemplateResponse(
            "auth/password_reset_confirm.html",
            {
                "request": request,
                "error": "Неверный или просроченный токен.",
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except InvalidPasswordException as err:
        return templates.TemplateResponse(
            "auth/password_reset_confirm.html",
            {
                "request": request,
                "error": str(err),
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return templates.TemplateResponse(
        "auth/password_reset_confirm.html",
        {
            "request": request,
            "message": "Пароль успешно сброшен.",
            "categories": categories,
        },
        status_code=status.HTTP_200_OK,
    )


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
    categories: Sequence[Category] = Depends(get_categories),
):
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


@router.get("/register", response_class=HTMLResponse)
async def register_form(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user:
        return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "categories": categories,
            "user": user,
        },
    )


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    categories: Sequence[Category] = Depends(get_categories),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    try:
        form = RegisterForm(
            username=username,
            email=email,
            password=password,
            password_confirm=password_confirm,
        )
    except ValidationError as err:
        errors_messages = [err["msg"] for err in err.errors()]
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "errors": errors_messages,
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_create = UserCreate(
            username=username, email=form.email, password=form.password
        )
        user = await user_manager.create(user_create)
    except UserAlreadyExists:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "errors": ["Пользователь с таким email уже существует"],
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except InvalidPasswordException as err:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "errors": [str(err)],
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "errors": [
                    "Произошла неизвестная ошибка. Пожалуйста, попробуйте позже"
                ],
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
