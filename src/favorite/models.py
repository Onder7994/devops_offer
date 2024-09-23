from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.auth.models import User
    from src.question.models import Question

class Favorite(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    question: Mapped["Question"] = relationship("Question")

    __table_args__ = (UniqueConstraint("user_id", "question_id", name="_user_question_uc"),)