from typing import Optional

from pydantic import BaseModel, ConfigDict
from src.category.schemas import CategoryRead


class QuestionBase(BaseModel):
    title: str
    category_id: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    # category_id: int


class QuestionReadBase(QuestionBase):
    id: int
    category: "CategoryRead"
    model_config = ConfigDict(from_attributes=True)


class QuestionReadNested(QuestionReadBase):
    pass


class QuestionRead(QuestionReadBase):
    answer: Optional["AnswerReadNested"]


from src.answer.schemas import AnswerReadNested

QuestionRead.model_rebuild()
