import re

from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError


class AdminLoginForm(BaseModel):
    email: str
    password: str

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
