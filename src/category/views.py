from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from . import Category
from .dependencies import (
    get_category_by_id_view,
    get_questions_by_category_id,
)
from src.db.database import db_helper
from src.config import settings
from src.auth.models import User
from src.auth.fastapi_users import fastapi_users
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.common.dependencies import get_categories

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix=settings.views.prefix_category,
    include_in_schema=False,
)


@router.get("/{category_id}", response_class=HTMLResponse)
async def view_single_category(
    request: Request,
    category_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(fastapi_users.current_user(optional=True))] = None,
    categories: Sequence[Category] = Depends(get_categories),
):
    category = await get_category_by_id_view(category_id=category_id, session=session)
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
        category_id=category_id, session=session
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
