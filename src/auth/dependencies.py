from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.manager import UserManager
from src.db.database import db_helper
from src.auth.models import User


async def get_user_db(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: Annotated["SQLAlchemyUserDatabase", Depends(get_user_db)]
):
    yield UserManager(user_db)
