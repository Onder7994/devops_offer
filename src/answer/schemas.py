from pydantic import BaseModel, ConfigDict


class AnswerBase(BaseModel):
    content: str
    question_id: int


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(BaseModel):
    content: str | None = None
    question_id: int | None


class AnswerReadBase(AnswerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AnswerReadNested(AnswerReadBase):
    pass

class AnswerRead(AnswerReadBase):
    question: "QuestionReadNested"
    model_config = ConfigDict(from_attributes=True)

from src.question.schemas import QuestionReadNested
AnswerRead.model_rebuild()