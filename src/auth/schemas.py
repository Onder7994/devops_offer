from pydantic import EmailStr, BaseModel, constr, field_validator, model_validator
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class RegisterForm(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    password_confirm: constr(min_length=6)

    @model_validator(mode="after")
    @classmethod
    def passwords_match(cls, model):
        if model.password != model.password_confirm:
            raise ValueError("Пароли не совпадают")
        return model
