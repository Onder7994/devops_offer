from typing import Annotated, List, Sequence

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.category.models import Category
from src.common.dependencies import get_categories
from src.config import settings
from src.auth.fastapi_users import current_active_user
from src.auth.models import User
from src.db.database import db_helper
from src.favorite.dependencies import get_user_favorites

templates = Jinja2Templates(directory="templates/auth")

router = APIRouter(prefix=settings.views.prefix_profile, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def profile(
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
    # favorites: List = Depends(get_user_favorites),
    categories: Sequence[Category] = Depends(get_categories),
):
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
        },
    )
