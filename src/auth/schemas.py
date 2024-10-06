import re

from pydantic import BaseModel, field_validator
from fastapi_users import schemas
from pydantic_core import PydanticCustomError


class UserRead(schemas.BaseUser[int]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str


class ResetPasswordForm(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, value):
            raise PydanticCustomError(
                "email_validate_error",
                "Некорректный формат email адреса",
            )
        return value
