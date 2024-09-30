from typing import Annotated, Sequence

from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserAlreadyExists
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from src.db.database import db_helper
from src.auth.dependencies import get_user_by_username
from src.auth.register.schemas import RegisterForm

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
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
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

    is_user_exist = await get_user_by_username(username=form.username, session=session)
    if is_user_exist:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "errors": ["Имя пользователя или email заняты"],
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
                "errors": ["Имя пользователя или email заняты"],
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
