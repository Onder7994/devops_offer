from typing import Annotated
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from .dependencies import (
    get_all_question,
    get_question_by_id,
    create_question,
    update_question,
)
from src.db.database import db_helper
from .schemas import QuestionUpdate, QuestionRead, QuestionCreate
from src.config import settings
from src.auth.fastapi_users import get_current_active_superuser

router = APIRouter(
    prefix=settings.api.prefix_question,
    tags=["Questions"],
)


@router.get("/", response_model=list[QuestionRead])
async def get_questions(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    questions = await get_all_question(session=session)
    return questions


@router.get("/{question_id}", response_model=QuestionRead)
async def get_question(
    question_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    question = await get_question_by_id(question_id=question_id, session=session)
    return question


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_new_question(
    question_in: QuestionCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(get_current_active_superuser)],
):
    new_question = await create_question(question_in=question_in, session=session)
    return new_question


@router.put("/{question_id}", response_model=QuestionRead)
async def update_existing_question(
    question_id: int,
    question_in: QuestionUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    updated_question = await update_question(
        question_id=question_id, question_in=question_in, session=session
    )
    return updated_question
