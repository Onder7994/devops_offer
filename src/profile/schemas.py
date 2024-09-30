from pydantic import BaseModel, model_validator, field_validator
from pydantic_core import PydanticCustomError
import re


class EditProfileForm(BaseModel):
    username: str
    email: str
    change_password: bool = False
    current_password: str | None = None
    new_password: str | None = None

    @field_validator("current_password", "new_password", mode="before")
    @classmethod
    def empty_strings_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

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

    @field_validator("current_password")
    @classmethod
    def validate_password(cls, value):
        if value is not None:
            if len(value) < 6:
                raise PydanticCustomError(
                    "password_validate_error",
                    "Пароль должен содержать не менее 6 символов",
                )
            return value

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):
        if value is not None:
            if len(value) < 6:
                raise PydanticCustomError(
                    "password_validate_error",
                    "Пароль должен содержать не менее 6 символов",
                )
            return value

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

    @model_validator(mode="after")
    @classmethod
    def validate_passwords(cls, model):
        if model.change_password:
            if not model.current_password:
                raise PydanticCustomError(
                    "current_password_error",
                    "Текущий пароль обязателен для изменения пароля.",
                )
            if not model.new_password:
                raise PydanticCustomError(
                    "new_password_error",
                    "Новый пароль обязателен для изменения пароля.",
                )
            if model.current_password == model.new_password:
                raise PydanticCustomError(
                    "change_password_compare_error",
                    "Пароли не должны совпадать!",
                )
        return model
