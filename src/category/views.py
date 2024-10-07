from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Request, Query
from math import ceil

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.schemas import PaginationQuery
from . import Category
from .dependencies import (
    get_category_by_slug,
    get_questions_by_category_id,
    get_questions_count_by_category_id,
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
)


@router.get("/{slug}", response_class=HTMLResponse)
async def view_single_category(
    request: Request,
    slug: str,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(current_active_user_ui)] = None,
    categories: Sequence[Category] = Depends(get_categories),
    page: str | None = Query(None),
    page_size: str | None = Query(None),
    search: str | None = Query(""),
):
    query_params: PaginationQuery = PaginationQuery()
    try:
        query_params = PaginationQuery(
            page=page,
            page_size=page_size,
        )
    except ValidationError:
        query_params.page = 1
        query_params.page_size = 9

    category = await get_category_by_slug(slug=slug, session=session)
    if category is None:
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "message": "Категория не найдена",
                "user": user,
                "categories": categories,
            },
        )
    offset = (query_params.page - 1) * query_params.page_size
    questions = await get_questions_by_category_id(
        category_id=category.id,
        session=session,
        offset=offset,
        limit=query_params.page_size,
        search=search,
    )
    total_questions = await get_questions_count_by_category_id(
        category_id=category.id,
        session=session,
        search=search,
    )
    total_pages = ceil(total_questions / query_params.page_size)
    return templates.TemplateResponse(
        "category_detail.html",
        {
            "request": request,
            "category": category,
            "questions": questions,
            "user": user,
            "categories": categories,
            "page": query_params.page,
            "page_size": query_params.page_size,
            "total_pages": total_pages,
            "search_query": search,
        },
    )
