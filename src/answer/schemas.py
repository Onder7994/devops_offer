from pydantic import BaseModel, ConfigDict, field_validator, field_serializer
from bs4 import BeautifulSoup


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
    @field_serializer("content")
    def strip_html(self, v):
        soup = BeautifulSoup(v, "html.parser")
        return soup.get_text()


class AnswerRead(AnswerReadBase):
    question: "QuestionReadNested"
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("content")
    def strip_html(self, v):
        soup = BeautifulSoup(v, "html.parser")
        return soup.get_text()


from src.question.schemas import QuestionReadNested

AnswerRead.model_rebuild()
