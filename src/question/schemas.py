from pydantic import BaseModel, ConfigDict


class QuestionBase(BaseModel):
    title: str
    category_id: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(QuestionBase):
    title: str | None = None
    category_id: int


class QuestionRead(QuestionBase):
    id: int
    title: str
    category_id: int
    category: "CategoryRead"
    answer: "AnswerRead"
    model_config = ConfigDict(from_attributes=True)


from src.answer.schemas import AnswerRead
from src.category.schemas import CategoryRead

QuestionRead.model_rebuild()
