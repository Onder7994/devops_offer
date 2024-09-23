from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.category.schemas import CategoryRead, CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status
from src.category.models import Category


async def get_all_category(session: AsyncSession) -> Sequence[Category]:
    stmt = select(Category).order_by(Category.id)
    result = await session.scalars(stmt)
    return result.all()


async def get_category_by_id(
    category_id: int, session: AsyncSession
) -> Category | None:
    stmt = select(Category).where(Category.id == category_id)
    result = await session.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found."
        )
    return category


async def create_category(
    category_in: CategoryCreate, session: AsyncSession
) -> Category:
    new_category = Category(
        name=category_in.name,
        description=category_in.description,
    )
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category


async def update_category(
    category_id: int, category_in: CategoryUpdate, session: AsyncSession
) -> Category:
    category = await get_category_by_id(category_id=category_id, session=session)
    for field, value in category_in.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category
