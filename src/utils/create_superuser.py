import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import asyncio
from fastapi_users.password import PasswordHelper
from sqlalchemy import select
from src.auth.models import User
from src.favorite.models import Favorite
from src.question.models import Question
from src.category.models import Category
from src.answer.models import Answer

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/devops_offer"
)
engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def create_superuser():
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    password = os.environ.get("ADMIN_PASSWORD", "admin")
    passwd_helper = PasswordHelper()
    hashed_password = passwd_helper.hash(password)
    stmt = select(User).where(User.email == email)

    async with async_session_maker() as session:
        result = await session.scalars(stmt)
        user = result.first()
        if user:
            logger.error(f"User with email %s already exists", email)
            return
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        logger.info("User %s created.", email)


if __name__ == "__main__":
    asyncio.run(create_superuser())
