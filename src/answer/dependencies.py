from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.answer.schemas import AnswerCreate, AnswerUpdate
from src.answer.models import Answer
from fastapi import HTTPException, status


async def get_all_answers(session: AsyncSession) -> Sequence[Answer]:
    stmt = select(Answer).order_by(Answer.id)
    result = await session.scalars(stmt)
    return result.all()


async def get_answer_by_id(answer_id: int, session: AsyncSession) -> Answer | None:
    stmt = (
        select(Answer).where(Answer.id == answer_id)
        # .options(selectinload(Answer.question))
    )
    result = await session.scalars(stmt)
    answer = result.first()
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found"
        )
    return answer


async def create_answer(answer_in: AnswerCreate, session: AsyncSession) -> Answer:
    new_answer = Answer(
        content=answer_in.content,
        question_id=answer_in.question_id,
    )
    session.add(new_answer)
    await session.commit()
    await session.refresh(new_answer)
    return new_answer


async def update_answer(
    answer_id: int, answer_in: AnswerUpdate, session: AsyncSession
) -> Answer:
    answer = await get_answer_by_id(answer_id=answer_id, session=session)
    for field, value in answer_in.model_dump(exclude_unset=True).items():
        setattr(answer, field, value)
    session.add(answer)
    await session.commit()
    await session.refresh(answer)
    return answer
