from typing import Annotated, Sequence

from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Request, Depends, status, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from src.category.dependencies import (
    get_all_category_with_pagination,
    get_total_category_count,
)
from src.question.dependencies import (
    get_total_questions_count,
    get_all_questions_with_pagination,
)
from src.common.schemas import PaginationQuery
from src.category.dependencies import delete_category_by_id
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
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    categories: Sequence[Category] = Depends(get_categories),
    questions: Sequence[Question] = Depends(get_all_questions),
    page: str | None = Query(None),
    page_size: str | None = Query(None),
    section: str = Query("categories"),
    success_category: str = Query(None),
    category_error: str = Query(None),
    success_question_answer: str = Query(None),
    question_answer_error: str = Query(None),
):

    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    query_params: PaginationQuery = PaginationQuery()
    try:
        query_params = PaginationQuery(
            page=page,
            page_size=page_size,
        )
    except ValidationError:
        query_params.page = 1
        query_params.page_size = 9

    categories_pagination = await get_all_category_with_pagination(
        session=session, page=query_params.page, limit=query_params.page_size
    )
    questions_pagination = await get_all_questions_with_pagination(
        session=session,
        page=query_params.page,
        limit=query_params.page_size,
    )
    total_categories = await get_total_category_count(session=session)
    total_questions = await get_total_questions_count(session=session)

    total_pages_categories = (
        total_categories + query_params.page_size - 1
    ) // query_params.page_size

    total_pages_questions = (
        total_questions + query_params.page_size - 1
    ) // query_params.page_size

    return templates.TemplateResponse(
        "admin/admin.html",
        {
            "request": request,
            "user": superuser,
            "categories": categories,
            "questions": questions,
            "categories_pagination": categories_pagination,
            "page": query_params.page,
            "page_size": query_params.page_size,
            "total_pages_categories": total_pages_categories,
            "questions_pagination": questions_pagination,
            "total_pages_questions": total_pages_questions,
            "section": section,
            "success_category": success_category,
            "category_error": category_error,
            "success_question_answer": success_question_answer,
            "question_answer_error": question_answer_error,
        },
    )


@router.post("/add_category", response_class=RedirectResponse)
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
            return RedirectResponse(
                url="/admin?section=categories&success_category=1",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        except HTTPException:
            return RedirectResponse(
                url="/admin?section=categories&category_error=Категория уже существует",
                status_code=status.HTTP_303_SEE_OTHER,
            )


@router.post("/add_question_answer", response_class=RedirectResponse)
async def admin_add_question_answer(
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    category_id: str = Form(...),
    question: str = Form(...),
    answer: str = Form(...),
):
    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    question_in = QuestionCreate(
        title=question,
        category_id=category_id,
    )
    try:
        new_question = await create_question(question_in=question_in, session=session)
    except HTTPException:
        return RedirectResponse(
            url="/admin?section=questions&question_answer_error=Вопрос уже существует",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    try:
        answer_in = AnswerCreate(
            content=answer,
            question_id=new_question.id,
        )
        await create_answer(answer_in=answer_in, session=session)
    except HTTPException:
        return RedirectResponse(
            url="/admin?section=questions&question_answer_error=Ответ уже существует",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(
        url="/admin?section=questions&success_question_answer=1",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/delete_question/{question_id}")
async def delete_question(
    question_id: int,
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    try:
        await delete_question_by_id(question_id=question_id, session=session)
    except HTTPException as err:
        print(err)
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)


@router.get("/delete_category/{category_id}")
async def delete_category(
    category_id: int,
    superuser: Annotated[User, Depends(current_active_superuser_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    if superuser is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    try:
        await delete_category_by_id(category_id=category_id, session=session)
    except HTTPException:
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
