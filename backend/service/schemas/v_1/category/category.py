from datetime import date
from typing import List, Optional

from pydantic import BaseModel, PositiveInt

from db import models

from ..user.user import User


class CategoryCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: models.CategoryTypeEnum

    class Config:
        use_enum_values = True


class Category(CategoryCreate):
    id: PositiveInt

    class Config:
        from_attributes = True


class Transaction(BaseModel):
    id: Optional[PositiveInt] = None
    currency: models.CurrencyEnum
    amount: float
    date: date
    note: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class CategoryTransactions(Category):
    user: User
    transaction: List[Transaction]
