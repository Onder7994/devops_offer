from typing import Annotated, Sequence

from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import (
    UserNotExists,
    InvalidResetPasswordToken,
)
from pydantic import ValidationError
from starlette.responses import RedirectResponse

from src.auth.schemas import ResetPasswordForm
from src.auth.models import User
from src.category import Category
from src.auth.fastapi_users import current_active_user_ui
from src.auth.manager import UserManager
from src.auth.dependencies import get_user_manager
from src.config import settings
from src.common.dependencies import get_categories


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_auth, include_in_schema=False)


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
    email: str = Form(...),
):
    try:
        valid_email = ResetPasswordForm(email=email)
        user = await user_manager.get_by_email(
            user_email=valid_email.email,
        )

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

    except ValidationError as err:
        errors_messages = [err["msg"] for err in err.errors()]
        print(errors_messages)
        return templates.TemplateResponse(
            "auth/password_reset.html",
            {
                "request": request,
                "errors": errors_messages,
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
    user: Annotated[User, Depends(current_active_user_ui)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user:
        return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

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
