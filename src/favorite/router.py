from fastapi import APIRouter, Depends, status
from typing import List, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.fastapi_users import current_active_user
from src.auth.models import User
from src.db.database import db_helper
from .dependencies import get_user_favorites, add_favorite, remove_favorite
from .schemas import FavoriteRead, FavoriteCreate
from src.config import settings

router = APIRouter(
    prefix=settings.api.prefix_favorites,
    tags=["Favorites"],
)


@router.get("", response_model=List[FavoriteRead])
async def get_favorites(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    favorites = await get_user_favorites(user=user, session=session)
    return favorites


@router.post("", response_model=FavoriteRead)
async def create_favorite(
    favorite_in: FavoriteCreate,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    favorite = await add_favorite(favorite_in=favorite_in, user=user, session=session)
    return favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: int,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    await remove_favorite(favorite_id=favorite_id, user=user, session=session)
