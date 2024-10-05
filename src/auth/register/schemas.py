import re

from pydantic import BaseModel, model_validator, field_validator
from pydantic_core import PydanticCustomError


def is_valid_password(password: str) -> bool:
    """
    Проверяет, соответствует ли пароль требованиям:
    - Минимальная длина 8 символов.
    - Содержит хотя бы одну заглавную букву.
    - Содержит хотя бы одну строчную букву.
    - Содержит хотя бы одну цифру.
    - Содержит хотя бы один специальный символ.
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


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
        if not is_valid_password(value):
            raise PydanticCustomError(
                "password_validate_error",
                "Пароль должен содержать не менее 8 символов, включая заглавные и строчные буквы, цифры и специальные символы.",
            )
        return value

    # @field_validator("password_confirm")
    # @classmethod
    # def validate_password_confirm(cls, value):
    #    if not is_valid_password(value):
    #        raise PydanticCustomError(
    #            "password_validate_error",
    #            "Пароль должен содержать не менее 8 символов, включая заглавные и строчные буквы, цифры и специальные символы.",
    #        )
    #    return value

    @model_validator(mode="after")
    @classmethod
    def passwords_match(cls, model):
        if model.password != model.password_confirm:
            raise PydanticCustomError(
                "password_compare_error",
                "Пароли не совпадают",
            )
        return model
