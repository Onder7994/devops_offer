import re

from pydantic import EmailStr, BaseModel, model_validator, field_validator
from pydantic_core import PydanticCustomError


class RegisterForm(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str

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

    @field_validator("username")
    @classmethod
    def validate_user(cls, value):
        if len(value) < 3:
            raise PydanticCustomError(
                "username_validate_error",
                "Имя пользователя должно содержать не менее 3 символов",
            )
        if len(value) > 25:
            raise PydanticCustomError(
                "username_validate_error",
                "Имя пользователя должно содержать не более 25 символов",
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise PydanticCustomError(
                "password_validate_error",
                "Пароль должен содержать не менее 6 символов",
            )
        return value

    @field_validator("password_confirm")
    @classmethod
    def validate_password_confirm(cls, value):
        if len(value) < 6:
            raise PydanticCustomError(
                "password_validate_error",
                "Пароль должен содержать не менее 6 символов",
            )
        return value

    @model_validator(mode="after")
    @classmethod
    def passwords_match(cls, model):
        if model.password != model.password_confirm:
            raise PydanticCustomError(
                "password_compare_error",
                "Пароли не совпадают",
            )
        return model
