from pydantic import EmailStr, BaseModel, constr, field_validator, model_validator
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str


class RegisterForm(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=6)
    password_confirm: constr(min_length=6)

    @model_validator(mode="after")
    @classmethod
    def passwords_match(cls, model):
        if model.password != model.password_confirm:
            raise ValueError("Пароли не совпадают")
        return model
