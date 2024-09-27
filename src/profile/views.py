from typing import Annotated, List, Sequence

from fastapi import APIRouter, Depends, Request
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

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_profile, include_in_schema=False)


@router.get("/", response_class=HTMLResponse, response_model=None)
async def profile(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    categories: Sequence[Category] = Depends(get_categories),
):
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
