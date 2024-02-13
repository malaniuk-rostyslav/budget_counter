from fastapi import APIRouter
from fastapi_pagination import add_pagination

root_router = APIRouter()

add_pagination(root_router)
