from datetime import date
from typing import Optional

from pydantic import BaseModel, PositiveInt

from db import models

from ..category.category import Category
from ..user.user import User


class TransactionCreate(BaseModel):
    amount: float
    date: date
    note: Optional[str] = None


class Transaction(TransactionCreate):
    id: PositiveInt
    currency: models.CurrencyEnum
    category: Category
    user: User

    class Config:
        use_enum_values = True
        from_attributes = True
