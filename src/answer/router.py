from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import (
    get_all_answers,
    get_answer_by_id,
    create_answer,
    update_answer,
)
from src.db.database import db_helper
from .schemas import AnswerRead, AnswerCreate, AnswerUpdate
from src.config import settings
from src.auth.fastapi_users import current_active_superuser
from src.auth.models import User

router = APIRouter(
    prefix=settings.api.prefix_answer,
    tags=["Answers"],
)


@router.get("", response_model=list[AnswerRead])
async def get_answers(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    answers = await get_all_answers(session=session)
    return answers


@router.get("/{answer_id}", response_model=AnswerRead)
async def get_answer(
    answer_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    answer = await get_answer_by_id(answer_id=answer_id, session=session)
    return answer


@router.post("", response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
async def create_new_answer(
    answer_in: AnswerCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: Annotated[User, Depends(current_active_superuser)],
):
    new_answer = await create_answer(answer_in=answer_in, session=session)
    return new_answer


@router.put("/{answer_id}", response_model=AnswerRead)
async def update_existing_answer(
    answer_id: int,
    answer_in: AnswerUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    _: Annotated[User, Depends(current_active_superuser)],
):
    updated_answer = await update_answer(
        answer_id=answer_id,
        answer_in=answer_in,
        session=session,
    )
    return updated_answer
