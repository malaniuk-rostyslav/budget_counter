from fastapi import APIRouter
from fastapi_pagination import add_pagination

from .auth import auth
from .category import category
from .user import user

root_router = APIRouter()

root_router.include_router(auth.router, tags=["auth"], prefix="/auth")
root_router.include_router(user.router, tags=["user"], prefix="/user")
root_router.include_router(category.router, tags=["category"], prefix="/category")


add_pagination(root_router)
