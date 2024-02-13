from enum import Enum


class CurrencyEnum(Enum):
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"


class CategoryTypeEnum(Enum):
    INCOME = "Income"
    EXPENSE = "Expense"


class JWTType(str, Enum):
    """JWT token types"""

    ACCESS = "access"
    REFRESH = "refresh"


PASSWORD_MIN = 8
PASSWORD_MAX = 150
