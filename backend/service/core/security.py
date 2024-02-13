from datetime import datetime, timedelta
from typing import Any, Final, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from service.core import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
HASH_ALGORITHM: Final[str] = "HS256"


def create_access_token(
    subject: Union[str, Any],
    type_: Optional[str] = "system",
    exp_delta: timedelta = None,
) -> str:
    """
    Create access JWT token for login into the system.
    """
    expire = datetime.utcnow() + timedelta(
        minutes=exp_delta if exp_delta else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"exp": expire, "sub": str(subject), "type": type_}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=HASH_ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def set_password_hash(password: str) -> str:
    return pwd_context.hash(password)
