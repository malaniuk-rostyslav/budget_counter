from enum import Enum


class CurrencyEnum(Enum):
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"


class CategoryTypeEnum(Enum):
    INCOME = "Income"
    EXPENSE = "Expense"
