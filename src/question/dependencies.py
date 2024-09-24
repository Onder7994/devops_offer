from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.category.dependencies import get_category_by_id
from src.question.schemas import QuestionRead, QuestionCreate, QuestionUpdate
from fastapi import HTTPException, status
from src.question.models import Question


async def get_all_question(session: AsyncSession) -> Sequence[Question]:
    stmt = (
        select(Question)
        .options(selectinload(Question.category))
        .options(selectinload(Question.answer))
        .order_by(Question.id)
    )
    result = await session.scalars(stmt)
    return result.all()


async def get_question_by_id(
    question_id: int, session: AsyncSession
) -> Question | None:
    stmt = (
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.category))
        .options(selectinload(Question.answer))
    )
    result = await session.scalars(stmt)
    question = result.first()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )
    return question


async def get_question_by_id_view(
    question_id: int, session: AsyncSession
) -> Question | None:
    stmt = (
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.category))
        .options(selectinload(Question.answer))
    )
    result = await session.scalars(stmt)
    question = result.first()
    return question


async def create_question(
    question_in: QuestionCreate, session: AsyncSession
) -> Question:
    is_category_exit = await get_category_by_id(
        category_id=question_in.category_id, session=session
    )
    if is_category_exit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )
    new_question = Question(
        title=question_in.title, category_id=question_in.category_id
    )
    session.add(new_question)
    await session.commit()
    await session.refresh(new_question)
    stmt = (
        select(Question)
        .options(
            selectinload(Question.category),
            selectinload(Question.answer),
        )
        .where(Question.id == new_question.id)
    )
    result = await session.scalars(stmt)
    question_with_relations = result.first()

    return question_with_relations


async def update_question(
    question_id: int, question_in: QuestionUpdate, session: AsyncSession
) -> Question:
    question = await get_question_by_id(question_id=question_id, session=session)
    for field, value in question_in.model_dump(exclude_unset=True).items():
        setattr(question, field, value)
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return question
