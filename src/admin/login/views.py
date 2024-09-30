from typing import Annotated, Sequence

from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_users.exceptions import UserNotExists
from pydantic import ValidationError
from starlette.responses import RedirectResponse

from src.admin.login.schemas import AdminLoginForm
from src.auth.models import User
from src.category import Category
from src.auth.fastapi_users import (
    auth_backend_cookie,
    current_active_superuser_ui,
    current_active_user_ui,
)
from src.auth.manager import UserManager
from src.auth.dependencies import get_user_manager
from src.config import settings
from src.common.dependencies import get_categories

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_admin_login, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def admin_login_form(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user:
        if superuser is None:
            return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "admin/admin_login.html",
        {
            "request": request,
            "categories": categories,
            "user": user,
        },
    )


@router.post("/", response_class=HTMLResponse)
async def admin_login(
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    email: str = Form(...),
    password: str = Form(...),
    categories: Sequence[Category] = Depends(get_categories),
):
    errors = []
    try:
        form = AdminLoginForm(
            email=email,
            password=password,
        )

    except ValidationError as err:
        errors_messages = [err["msg"] for err in err.errors()]
        return templates.TemplateResponse(
            "admin/admin_login.html",
            {
                "request": request,
                "errors": errors_messages,
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        is_superuser = await user_manager.get_by_email(user_email=form.email)
        if is_superuser.is_superuser is False:
            errors.append("Вход только для администраторов")
    except UserNotExists:
        errors.append("Вход только для администраторов")

    if errors:
        return templates.TemplateResponse(
            "admin/admin_login.html",
            {
                "request": request,
                "errors": errors,
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = await user_manager.authenticate(
        credentials=OAuth2PasswordRequestForm(
            username=form.email, password=form.password, scope=""
        )
    )

    strategy = auth_backend_cookie.get_strategy()
    token = await strategy.write_token(user)
    response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
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
