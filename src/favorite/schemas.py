from pydantic import BaseModel, ConfigDict

class FavoriteBase(BaseModel):
    question_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteRead(FavoriteBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)