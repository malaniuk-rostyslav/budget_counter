from typing import Optional

from pydantic import BaseModel, PositiveInt

from db import models


class CategoryCreate(BaseModel):
    id: PositiveInt
    title: str
    description: Optional[str] = None
    type: models.CategoryTypeEnum

    class Config:
        use_enum_values = True


class Category(CategoryCreate):
    pass

    class Config:
        from_attributes = True
