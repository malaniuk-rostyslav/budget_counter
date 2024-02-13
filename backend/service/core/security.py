from datetime import datetime, timedelta
from typing import Final, Union

from jose import jwt
from passlib.context import CryptContext

from db.models import JWTType
from service.core import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

HASH_ALGORITHM: Final[str] = "HS256"


def create_jwt_token(pk: Union[int, str], jwt_type: JWTType = JWTType.ACCESS) -> str:
    """
    Create access JWT token for login into the system
    """
    expired_times: dict = {
        JWTType.ACCESS: settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        JWTType.REFRESH: settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
    }
    expire = datetime.utcnow() + timedelta(
        minutes=expired_times.get(
            jwt_type.value, settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    to_encode = {
        "pk": str(pk),
        "exp": expire,
        "type": jwt_type.value,
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.HASH_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def set_password_hash(password: str) -> str:
    return pwd_context.hash(password)
