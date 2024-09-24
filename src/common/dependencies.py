from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from src.category.dependencies import get_all_category
from src.db.database import db_helper


async def get_categories(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Sequence:
    return await get_all_category(session=session)
