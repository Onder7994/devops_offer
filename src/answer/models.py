from sqlalchemy import Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.question.models import Question


class Answer(Base):
    __table_args__ = (UniqueConstraint("question_id", name="uq_answers_question_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), unique=True)

    question: Mapped["Question"] = relationship("Question", back_populates="answer")
