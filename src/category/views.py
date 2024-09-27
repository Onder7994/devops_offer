from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from . import Category
from .dependencies import (
    get_category_by_slug,
    get_questions_by_category_id,
)
from src.db.database import db_helper
from src.config import settings
from src.auth.models import User
from src.auth.fastapi_users import current_active_user_ui
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.common.dependencies import get_categories

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix=settings.views.prefix_category,
    include_in_schema=False,
)


@router.get("/{slug}", response_class=HTMLResponse)
async def view_single_category(
    request: Request,
    slug: str,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(current_active_user_ui)] = None,
    categories: Sequence[Category] = Depends(get_categories),
):
    category = await get_category_by_slug(slug=slug, session=session)
    if category is None:
        return templates.TemplateResponse(
            "404.html",
            {
                "request": request,
                "message": "Категория не найдена",
                "user": user,
                "categories": categories,
            },
        )
    questions = await get_questions_by_category_id(
        category_id=category.id, session=session
    )
    return templates.TemplateResponse(
        "category_detail.html",
        {
            "request": request,
            "category": category,
            "questions": questions,
            "user": user,
            "categories": categories,
        },
    )
