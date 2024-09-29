from typing import Annotated, List, Sequence

from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.category.models import Category
from src.common.dependencies import get_categories
from src.config import settings
from src.auth.fastapi_users import current_active_user_ui
from src.auth.models import User
from src.db.database import db_helper
from src.favorite.dependencies import get_user_favorites
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_profile, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def profile(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    favorites = await get_user_favorites(user=user, session=session)
    return templates.TemplateResponse(
        "auth/profile.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
            "favorites": favorites,
        },
    )


@router.get("/edit", response_class=HTMLResponse)
async def edit_profile(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "auth/edit_profile.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
        },
    )
