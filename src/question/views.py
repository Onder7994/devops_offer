from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.category.models import Category
from src.question.dependencies import get_question_by_slug
from src.db.database import db_helper
from src.config import settings
from src.auth.models import User
from src.auth.fastapi_users import current_active_user_ui
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.common.dependencies import get_categories

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix=settings.views.prefix_question,
    include_in_schema=False,
)


@router.get("/{slug}", response_class=HTMLResponse)
async def view_single_question(
    request: Request,
    slug: str,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(current_active_user_ui)] = None,
    categories: Sequence[Category] = Depends(get_categories),
):
    question = await get_question_by_slug(slug=slug, session=session)
    if question is None:
        return templates.TemplateResponse(
            "404.html",
            {
                "request": request,
                "message": "Вопрос не найден",
                "user": user,
                "categories": categories,
            },
        )
    return templates.TemplateResponse(
        "question_detail.html",
        {
            "request": request,
            "question": question,
            "categories": categories,
            "user": user,
        },
    )
