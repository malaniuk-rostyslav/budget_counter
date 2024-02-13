from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, SecretStr

from db import models


class AuthForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        email: EmailStr = Form(...),
        password: SecretStr = Form(
            ..., min_length=models.PASSWORD_MIN, max_length=models.PASSWORD_MAX
        ),
    ):
        self.email = email
        self.password = password
