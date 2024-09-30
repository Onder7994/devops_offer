from typing import Annotated, Sequence

from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_users.exceptions import UserNotExists
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from src.db.database import db_helper
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

router = APIRouter(prefix=settings.views.prefix_admin, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def admin_ui(
    request: Request,
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "admin/admin.html",
        {
            "request": request,
            "user": superuser,
            "categories": categories,
        },
    )
