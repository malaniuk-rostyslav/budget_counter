import os
from datetime import date
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PositiveInt, RedisDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ###########
    # PROJECT #
    ###########
    PROJECT_NAME: str = "Budget Counter"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "very_secret_key")
    HTTP_SERVER: AnyHttpUrl
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", True)

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    ############
    # DATABASE #
    ############
    DB_SERVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: int
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    CELERY_SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return "postgresql+psycopg2://{}:{}@{}:5432/{}".format(
            values.get("DB_USER"),
            values.get("DB_PASSWORD"),
            values.get("DB_SERVER"),
            values.get("DB_NAME"),
        )

    @validator("CELERY_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_celery_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return "postgresql+psycopg2://{}:{}@{}:5432/{}".format(
            values.get("DB_USER"),
            values.get("DB_PASSWORD"),
            values.get("DB_SERVER"),
            values.get("DB_NAME"),
        )

    #######
    # JWT #
    #######
    JWT_TOKEN_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 60 minutes
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day

    # 60 sec * 60 min * 24 hour = 1 day
    VERIFICATION_TOKEN_LIFETIME: PositiveInt = 60 * 60 * 24

    #########
    # ADMIN #
    #########
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_BIRTHDAY: date

    ############
    # REDIS #
    ############
    REDIS_URL: RedisDsn

    class Config:
        case_sensitive = True


settings = Settings()
