from pydantic import EmailStr, BaseModel, constr, field_validator
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
    password_confirm: str

    @field_validator("password_confirm")
    @classmethod
    def password_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Пароли не совпадают")
        return v
