from pydantic import BaseModel, EmailStr, model_validator, constr


class EditProfileForm(BaseModel):
    username: constr(min_length=3, max_length=25)
    email: EmailStr
    current_password: constr(min_length=6)
    new_password: constr(min_length=6)

    @model_validator(mode="after")
    @classmethod
    def passwords_match(cls, model):
        if model.current_password == model.new_password:
            raise ValueError("Пароли не должны совпадать!")
        return model
