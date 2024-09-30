from pydantic import BaseModel, EmailStr, model_validator, constr, field_validator


class EditProfileForm(BaseModel):
    username: constr(min_length=3, max_length=25)
    email: EmailStr
    change_password: bool = False
    current_password: constr(min_length=6) | None = None
    new_password: constr(min_length=6) | None = None

    @field_validator("current_password", "new_password", mode="before")
    @classmethod
    def empty_strings_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @model_validator(mode="after")
    @classmethod
    def validate_passwords(cls, model):
        if model.change_password:
            if not model.current_password:
                raise ValueError("Текущий пароль обязателен для изменения пароля.")
            if not model.new_password:
                raise ValueError("Новый пароль обязателен для изменения пароля.")
            if model.current_password == model.new_password:
                raise ValueError("Пароли не должны совпадать!")
        return model
