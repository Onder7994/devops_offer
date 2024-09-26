from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str | None = None
    description: str | None = None


class CategoryRead(CategoryBase):
    id: int
    name: str
    description: str
    slug: str
    model_config = ConfigDict(from_attributes=True)
