from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import selectinload

from src.question.models import Question
from src.favorite.models import Favorite
from src.favorite.schemas import FavoriteCreate
from src.auth.models import User


async def get_user_favorites(user: User, session: AsyncSession):
    stmt = (
        select(Favorite)
        .where(Favorite.user_id == user.id)
        .options(selectinload(Favorite.question).selectinload(Question.category))
    )
    result = await session.scalars(stmt)
    return result.all()


async def get_all_favorites_with_pagination(
    user: User, session: AsyncSession, page: int = 1, limit: int = 9
):
    offset = (page - 1) * limit
    stmt = (
        select(Favorite)
        .where(Favorite.user_id == user.id)
        .options(selectinload(Favorite.question).selectinload(Question.category))
        .order_by(desc(Favorite.id))
        .offset(offset)
        .limit(limit)
    )
    result = await session.scalars(stmt)
    return result.all()


async def get_total_favorites_count(user: User, session: AsyncSession):
    stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user.id)
    result = await session.execute(stmt)
    return result.scalar()


async def add_favorite(favorite_in: FavoriteCreate, user: User, session: AsyncSession):
    favorite = Favorite(user_id=user.id, question_id=favorite_in.question_id)
    session.add(favorite)
    try:
        await session.commit()
        await session.refresh(favorite)
        return favorite
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Favorite already exists."
        )


async def remove_favorite(favorite_id: int, user: User, session: AsyncSession):
    stmt = select(Favorite).where(
        Favorite.id == favorite_id, Favorite.user_id == user.id
    )
    result = await session.scalars(stmt)
    favorite = result.first()
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found.",
        )
    await session.delete(favorite)
    await session.commit()
