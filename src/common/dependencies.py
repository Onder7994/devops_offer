from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.question import Question
from src.category import Category
from src.category.dependencies import get_all_category
from src.question.dependencies import get_all_question
from src.db.database import db_helper


async def get_categories(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Sequence:
    return await get_all_category(session=session)


async def get_all_questions(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Sequence:
    return await get_all_question(session=session)
