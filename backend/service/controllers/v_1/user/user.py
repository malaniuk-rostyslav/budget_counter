from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import UJSONResponse

from db import manager
from db.session import DBSession
from service.core.dependencies import get_db
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
