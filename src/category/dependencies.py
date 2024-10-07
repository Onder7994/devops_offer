from typing import Sequence, List

from slugify import slugify
from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.question.models import Question
from src.category.schemas import CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status
from src.category.models import Category


async def get_all_category(session: AsyncSession) -> Sequence[Category]:
    stmt = select(Category).order_by(Category.id)
    result = await session.scalars(stmt)
    return result.all()


async def get_all_category_with_pagination(
    session: AsyncSession, page: int = 1, limit: int = 9
) -> Sequence[Category]:
    offset = (page - 1) * limit
    stmt = select(Category).order_by(Category.id).offset(offset).limit(limit)
    result = await session.scalars(stmt)
    return result.all()


async def get_total_category_count(session: AsyncSession):
    stmt = select(func.count(Category.id))
    result = await session.execute(stmt)
    return result.scalar()


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


async def get_category_by_id_view(
    category_id: int, session: AsyncSession
) -> Category | None:
    stmt = select(Category).where(Category.id == category_id)
    result = await session.scalars(stmt)
    category = result.first()
    return category


async def get_category_by_slug(slug: str, session: AsyncSession) -> Category | None:
    stmt = select(Category).where(Category.slug == slug)
    result = await session.scalars(stmt)
    category = result.first()
    return category


async def create_category(
    category_in: CategoryCreate, session: AsyncSession
) -> Category:
    slug = slugify(category_in.name)
    is_category_exist = await get_category_by_slug(slug=slug, session=session)
    if is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exist",
        )
    new_category = Category(
        name=category_in.name,
        slug=slug,
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
    slug = slugify(category_in.name)
    is_category_exist = await get_category_by_slug(slug=slug, session=session)
    if is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exist",
        )
    category_in.slug = slug
    for field, value in category_in.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def get_questions_by_category_id(
    category_id: int,
    session: AsyncSession,
    offset: int = 0,
    limit: int = 9,
    search: str | None = None,
) -> Sequence[Question]:
    stmt = select(Question).where(Question.category_id == category_id)
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(Question.title.ilike(search_term))
    stmt = stmt.order_by(desc(Question.id)).offset(offset).limit(limit)
    result = await session.scalars(stmt)
    return result.all()


async def get_questions_count_by_category_id(
    category_id: int,
    session: AsyncSession,
    search: str | None = None,
) -> int:
    stmt = (
        select(func.count())
        .select_from(Question)
        .where(Question.category_id == category_id)
    )
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(Question.title.ilike(search_term))
    result = await session.execute(stmt)
    total = result.scalar_one()
    return total


async def delete_category_by_id(category_id: int, session: AsyncSession):
    stmt = (
        select(Category)
        .where(Category.id == category_id)
        .options(selectinload(Category.questions))
    )
    result = await session.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    if category.questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't delete category with existing questions",
        )
    await session.delete(category)
    await session.commit()
    return category
