from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import UJSONResponse
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError

from db import models
from db.session import DBSession
from service.core.dependencies import get_db, get_request_device_info
from service.core.security import create_jwt_token, verify_password
from service.schemas import v_1 as schemas_v_1

router = APIRouter()


def authenticate(db: DBSession, email: str, password: str) -> Optional[models.User]:
    user = db.query(models.User).filter(models.User.email == email).one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong credentials",
        )
    return user


def setup_request_user_device(
    db: DBSession, user: models.User, user_device: schemas_v_1.UserAgentDevice
):
    device = db.query(models.Device).filter(models.Device.user_id == user.id)
    if not user_device.fcm_token:
        if device.all():
            db.execute(
                update(models.Device)
                .where(models.Device.user_id == user.id)
                .values({"last_login": datetime.utcnow()})
            )
            db.flush()
            return
        device = models.Device(
            user_id=user.id,
            last_login=datetime.utcnow(),
            **user_device.model_dump(exclude_none=True),
        )
        db.add(device)
        db.flush()
        return
    device = db.query(models.Device).filter(
        models.Device.fcm_token == user_device.fcm_token
    )
    if device.one_or_none():
        if device.one_or_none().user_id == user.id:
            db.execute(
                update(models.Device)
                .where(models.Device.user_id == user.id)
                .values({"last_login": datetime.utcnow()})
            )
            db.flush()
    if device.one_or_none() and device.one_or_none().user_id != user.id:
        device.delete()
        db.flush()
        device = models.Device(
            user_id=user.id, last_login=datetime.utcnow(), **user_device.model_dump()
        )
        db.add(device)
        db.flush()
    elif not device.one_or_none():
        now = datetime.utcnow()
        device = models.Device(
            user_id=user.id, last_login=now, **user_device.model_dump()
        )
        db.add(device)
        db.flush()


@router.post("/login", response_model=schemas_v_1.JWTTokensResponse)
async def login(
    db: DBSession = Depends(get_db),
    user_device: schemas_v_1.UserAgentDevice = Depends(get_request_device_info),
    form_data: schemas_v_1.AuthForm = Depends(),
) -> Dict[str, str]:
    """
    OAuth2 compatible token login, get tokens for future requests \n
    FORM data: \n
    `email`: EmailStr \n
    `password`: str \n
    Responses: \n
    `200` OK - Everything is good (SUCCESS Response) \n
    `400` BAD REQUEST - Wrong credentials \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation
    """

    try:
        user = authenticate(db, form_data.email, form_data.password.get_secret_value())
    except (SQLAlchemyError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    access_token = create_jwt_token(user.id, jwt_type=models.JWTType.ACCESS)
    refresh_token = create_jwt_token(user.id, jwt_type=models.JWTType.REFRESH)
    setup_request_user_device(db, user, user_device)
    db.commit()
    return UJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        },
    )
