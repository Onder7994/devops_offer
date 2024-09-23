from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base
from fastapi_users.db import SQLAlchemyBaseUserTable
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.favorite.models import Favorite

class User(Base, SQLAlchemyBaseUserTable[int]):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)

    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user")