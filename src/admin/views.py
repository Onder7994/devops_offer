from typing import Annotated, Sequence

from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from src.question.models import Question
from src.question.schemas import QuestionCreate
from src.question.dependencies import create_question, delete_question_by_id
from src.answer.schemas import AnswerCreate
from src.answer.dependencies import create_answer
from src.category.schemas import CategoryCreate
from src.db.database import db_helper
from src.auth.models import User
from src.category import Category
from src.category.dependencies import create_category
from src.auth.fastapi_users import (
    current_active_superuser_ui,
)
from src.config import settings
from src.common.dependencies import get_categories, get_all_questions

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_admin, include_in_schema=False)


@router.get("", response_class=HTMLResponse)
async def admin_ui(
    request: Request,
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    categories: Sequence[Category] = Depends(get_categories),
    questions: Sequence[Question] = Depends(get_all_questions),
):
    error = request.query_params.get("error")
    success = request.query_params.get("success")
    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "admin/admin.html",
        {
            "request": request,
            "user": superuser,
            "categories": categories,
            "questions": questions,
            "category_error": error,
            "success_category": success,
        },
    )


@router.post("/add_category", response_class=HTMLResponse)
async def admin_add_category(
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    category: str = Form(...),
):
    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    if category:
        category_in = CategoryCreate(name=category)
        try:
            await create_category(category_in=category_in, session=session)
        except HTTPException:
            return RedirectResponse(
                url="/admin?error=Категория уже существует",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        return RedirectResponse(url="/admin?success=Категория добавлена")


@router.post("/add_question_answer", response_class=HTMLResponse)
async def admin_add_question_answer(
    request: Request,
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    categories: Sequence[Category] = Depends(get_categories),
    questions: Sequence[Question] = Depends(get_all_questions),
    category_id: str = Form(...),
    question: str = Form(...),
    answer: str = Form(...),
):
    question_in = QuestionCreate(
        title=question,
        category_id=category_id,
    )
    try:
        new_question = await create_question(question_in=question_in, session=session)
    except HTTPException:
        return templates.TemplateResponse(
            "admin/admin.html",
            {
                "request": request,
                "user": superuser,
                "categories": categories,
                "question_answer_error": "Вопрос уже существует",
                "questions": questions,
            },
            status_code=status.HTTP_200_OK,
        )
    try:
        answer_in = AnswerCreate(
            content=answer,
            question_id=new_question.id,
        )
        await create_answer(answer_in=answer_in, session=session)
    except HTTPException:
        return templates.TemplateResponse(
            "admin/admin.html",
            {
                "request": request,
                "user": superuser,
                "categories": categories,
                "question_answer_error": "Ответ уже существует",
                "questions": questions,
            },
            status_code=status.HTTP_200_OK,
        )
    return templates.TemplateResponse(
        "admin/admin.html",
        {
            "request": request,
            "user": superuser,
            "categories": categories,
            "success_question_answer": True,
            "questions": questions,
        },
    )


@router.get("/delete_question/{question_id}")
async def delete_question(
    request: Request,
    question_id: int,
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    categories: Sequence[Category] = Depends(get_categories),
    questions: Sequence[Question] = Depends(get_all_questions),
):
    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    await delete_question_by_id(question_id=question_id, session=session)
    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
