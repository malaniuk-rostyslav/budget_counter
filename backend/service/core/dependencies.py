from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from starlette import status

from db import manager, models
from db.session import DBSession

from ..schemas.v_1 import JWTTokenPayload, UserAgentDevice
from . import settings
from .security import HASH_ALGORITHM

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)


async def get_db() -> Generator:
    with DBSession() as session:
        yield session


async def get_current_user(
    db: DBSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> Optional[models.User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[HASH_ALGORITHM])
        JWTTokenPayload(pk=payload["pk"], type=models.JWTType.ACCESS.value)
    except (jwt.JWTError, ValidationError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user = await manager.get_user(db, id=int(payload["pk"]))
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )


def get_request_device_info(request: Request):
    try:
        device = UserAgentDevice(
            fcm_token=request.headers.get("FCM-Token", ""),
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not valid User-Agent format",
        )
    return device
