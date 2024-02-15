from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import UJSONResponse

from db import manager, models
from db.session import DBSession
from service.core.dependencies import get_current_user, get_db
from service.core.security import create_jwt_token
from service.schemas import v_1 as schemas_v_1

router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_v_1.User,
)
async def sign_up(
    input_data: schemas_v_1.UserCreate,
    db: DBSession = Depends(get_db),
) -> UJSONResponse:
    """
    User sign up \n
    JSON data \n
    `email`: EmailStr \n
    `birthday`: Optional[date] \n
    `password`: str \n
    `password_confirm`: str \n
    Responses: \n
    `201` CREATED \n
    `400` BAD REQUEST - User with this email exists \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation \n
    """
    user_data = {
        "email": input_data.email,
        "password": input_data.password,
        "birthday": input_data.birthday,
    }
    user = await manager.create_user(db, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with {input_data.email} email, already exist",
        )
    db.commit()
    db.refresh(user)
    create_jwt_token(user.id)
    return user


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=schemas_v_1.User,
)
async def get_my_user_info(
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    User sign up \n
    JSON data \n
    `email`: EmailStr \n
    `birthday`: Optional[date] \n
    `password`: str \n
    `password_confirm`: str \n
    Responses: \n
    `201` CREATED \n
    `400` BAD REQUEST - User with this email exists \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation \n
    """
    user = db.query(models.User).filter(models.User.id == current_user.id).one_or_none()
    return user


@router.patch(
    "/currency/",
    status_code=status.HTTP_200_OK,
    response_model=schemas_v_1.User,
)
async def update_currency(
    input_data: schemas_v_1.UserCurrencyUpdate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Update currency \n
    JSON data \n
    `currency`: CurrencyEnum \n
    `cross_course`: float \n
    Responses: \n
    `200` OK \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation \n
    """
    us = db.query(models.UserSettings).filter(
        models.UserSettings.user_id == current_user.id
    )
    us.update({"currency": input_data.currency})
    return current_user


@router.patch(
    "/notifications/",
    status_code=status.HTTP_200_OK,
    response_model=schemas_v_1.User,
)
async def update_notifications(
    input_data: schemas_v_1.UserNotificationsUpdate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Update currency \n
    JSON data \n
    `currency`: CurrencyEnum \n
    `cross_course`: float \n
    Responses: \n
    `200` OK \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation \n
    """
    us = db.query(models.UserSettings).filter(
        models.UserSettings.user_id == current_user.id
    )
    us.update({"notification_on": input_data.notification_on})
    return current_user
