from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import (
    get_all_category,
    get_category_by_id,
    create_category,
    update_category,
)
from src.db.database import db_helper
from .schemas import CategoryRead, CategoryUpdate, CategoryCreate
from src.config import settings

router = APIRouter(
    prefix=settings.api.prefix_category,
    tags=["Categories"],
)


@router.get("/", response_model=list[CategoryRead])
async def get_categories(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    categories = await get_all_category(session=session)
    return categories


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    category = await get_category_by_id(category_id=category_id, session=session)
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category_in: CategoryCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    new_category = await create_category(category_in=category_in, session=session)
    return new_category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_existing_category(
    category_in: CategoryUpdate,
    category_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    updated_category = await update_category(
        category_id=category_id, category_in=category_in, session=session
    )
    return updated_category
