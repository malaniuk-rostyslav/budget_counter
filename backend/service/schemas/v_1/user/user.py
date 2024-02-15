from datetime import date, datetime
from typing import Optional

from pydantic import (BaseModel, EmailStr, Field, PositiveInt, model_validator,
                      validator)

from db import models


class UserCurrencyUpdate(BaseModel):
    currency: models.CurrencyEnum
    cross_course: float

    class Config:
        use_enum_values = True


class UserNotificationsUpdate(BaseModel):
    notification_on: bool


class UserSettings(BaseModel):
    id: PositiveInt
    notification_on: bool
    currency: models.CurrencyEnum

    class Config:
        use_enum_values = True
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    birthday: Optional[date] = None

    @validator("birthday")
    def birthday_validation(cls, value):
        if value > datetime.today().date():
            raise ValueError(f"Your birthday can not be after today")
        return value


class UserCreate(UserBase):
    password: str = Field(min_length=models.PASSWORD_MIN)
    password_confirm: str = Field(min_length=models.PASSWORD_MIN)

    @model_validator(mode="before")
    def validate_passwords(cls, values):
        if values.get("password") != values.get("password_confirm"):
            raise ValueError("Password mismatch")
        return values


class User(BaseModel):
    id: PositiveInt
    email: EmailStr
    birthday: Optional[date]
    settings: UserSettings

    class Config:
        from_attributes = True


class UserAgentDevice(BaseModel):
    fcm_token: Optional[str]
