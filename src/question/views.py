from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.category.models import Category
from src.question.dependencies import get_question_by_id_view
from src.db.database import db_helper
from src.config import settings
from src.auth.models import User
from src.auth.fastapi_users import fastapi_users
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.common.dependencies import get_categories

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix=settings.views.prefix_question,
    include_in_schema=False,
)


@router.get("/{question_id}", response_class=HTMLResponse)
async def view_single_question(
    request: Request,
    question_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(fastapi_users.current_user(optional=True))] = None,
    categories: Sequence[Category] = Depends(get_categories),
):
    question = await get_question_by_id_view(question_id=question_id, session=session)
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
