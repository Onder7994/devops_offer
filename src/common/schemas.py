from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError


class PaginationQuery(BaseModel):
    page: int = 1
    page_size: int = 9

    @field_validator("page", mode="before")
    @classmethod
    def page_validate(cls, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 1

        if value == 0:
            raise PydanticCustomError(
                "page_validate_error",
                "Страница не может быть равна нулю",
            )
        if value < 0:
            raise PydanticCustomError(
                "page_validate_error",
                "Страница не может быть равна отрицательным числом",
            )

        return value

    @field_validator("page_size")
    @classmethod
    def page_size_validate(cls, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 9

        if value == 0:
            raise PydanticCustomError(
                "page_size_validate_error",
                "Размер страницы не может быть равна нулю",
            )
        if value < 0:
            raise PydanticCustomError(
                "page_size_validate_error",
                "Размер страницы не может быть равна отрицательным числом",
            )
        if value > 50:
            raise PydanticCustomError(
                "page_size_validate_error",
                "Размер страницы не может быть больше 50",
            )
        return value
