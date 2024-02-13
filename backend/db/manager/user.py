from typing import Dict, Optional

from db.models import User
from db.session import DBSession
from service.core.security import set_password_hash


async def instance_exist(db: DBSession, model, **kwargs) -> bool:
    """Obtain Model name, fields as kwargs and check exist Instance or not"""
    is_exist = db.query(db.query(model).filter_by(**kwargs).exists()).scalar()
    return is_exist


async def get_user(db: DBSession, **kwargs) -> Optional[User]:
    """Obtain fields as kwargs and return active User instance or None"""
    user = db.query(User).filter_by(**kwargs).one_or_none()
    if not user:
        return
    return user


async def create_user(db: DBSession, user_data: Dict, **kwargs) -> Optional[User]:
    """Obtain new User fields, check exist User, set hash password and save"""
    exist = await instance_exist(db, model=User, email=user_data["email"])
    if exist:
        return
    password = set_password_hash(password=user_data.pop("password"))
    user = User(**user_data, hashed_password=password, **kwargs)
    db.add(user)
    db.flush()
    return user
