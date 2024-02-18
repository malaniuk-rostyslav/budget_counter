from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt, model_validator

from db import models

from ..category.category import Category
from ..user.user import User


class TransactionCreate(BaseModel):
    amount: float
    date: date
    note: Optional[str] = None


class TransactionOnCreate(TransactionCreate):
    id: PositiveInt
    currency: models.CurrencyEnum
    user: User

    class Config:
        use_enum_values = True
        from_attributes = True


class Transaction(TransactionCreate):
    id: PositiveInt
    currency: models.CurrencyEnum
    category: Category
    user: User

    class Config:
        use_enum_values = True
        from_attributes = True


class TransactionCurrencyUpdate(BaseModel):
    currency_to_update: models.CurrencyEnum
    currency_to_replace: models.CurrencyEnum
    cross_course: float
    start_date: date
    end_date: date

    class Config:
        use_enum_values = True

    @model_validator(mode="before")
    def validate_fields_amount(cls, values):
        if len(values) == 2 or len(values) == 3:
            raise ValueError(
                "cross_course, start_date, end_date are fields that are either all or none of them passed",
            )
        return values

    @model_validator(mode="before")
    def validate_date(cls, values):
        if values.get("start_date") and values.get("end_date"):
            if (
                values.get("start_date") > values.get("end_date")
                or datetime.strptime(values.get("end_date"), "%Y-%m-%d").date()
                > date.today()
            ):
                raise ValueError(
                    "wrong date",
                )
        return values
