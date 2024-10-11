import json
from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Request, status, Form, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from src.favorite.dependencies import add_favorite, get_user_favorites
from src.favorite.schemas import FavoriteCreate
from src.question.dependencies import get_question_by_id
from src.category.models import Category
from src.question.dependencies import get_question_by_slug, update_question_counter
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
    error: str = Query(None),
    success: str = Query(None),
):
    favorite_question_ids = []
    question = await get_question_by_slug(slug=slug, session=session)
    if question is None:
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "message": "Вопрос не найден",
                "user": user,
                "categories": categories,
                "error": error,
                "success": success,
                "favorite_question_ids": favorite_question_ids,
            },
        )
    if user:
        favorites = await get_user_favorites(user=user, session=session)
        favorite_question_ids = [favorite.question_id for favorite in favorites]
    await update_question_counter(slug=slug, session=session)
    return templates.TemplateResponse(
        "question_detail.html",
        {
            "request": request,
            "question": question,
            "categories": categories,
            "user": user,
            "error": error,
            "success": success,
            "favorite_question_ids": favorite_question_ids,
        },
    )


@router.post("/add_to_favorites", response_class=RedirectResponse)
async def add_to_favorites(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(current_active_user_ui)] = None,
    question_id: int = Form(...),
):
    if user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    try:
        question = await get_question_by_id(question_id=question_id, session=session)
        question_slug = question.slug
        favorite_in = FavoriteCreate(
            question_id=question_id,
        )
        await add_favorite(favorite_in=favorite_in, user=user, session=session)
        return RedirectResponse(
            url=f"/questions/{question.slug}?success=Добавлено в избранное",
            status_code=status.HTTP_302_FOUND,
        )
    except HTTPException:
        return RedirectResponse(
            url=f"/questions/{question_slug}?error=Уже в избранном",
            status_code=status.HTTP_303_SEE_OTHER,
        )
