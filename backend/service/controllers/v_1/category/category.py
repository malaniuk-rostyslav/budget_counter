from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import UJSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import PositiveInt
from sqlalchemy import and_, exists

from db import models
from db.session import DBSession
from service.core.dependencies import get_current_user, get_db
from service.schemas import v_1 as schemas_v_1

from ..utils import category_tr_filter_search, search_enum_check

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_v_1.Category,
)
async def create_category(
    input_data: schemas_v_1.CategoryCreate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Create category \n
    JSON data \n
    `title`: str \n
    `description`: Optional[str] \n
    `type`: CategoryTypeEnum \n
    Responses: \n
    `201` CREATED \n
    `400` BAD REQUEST - Category already exists in your list \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation
    """
    category_exists = db.query(
        exists().where(
            and_(
                models.Category.title == input_data.title,
                models.Category.user_id == current_user.id,
                models.Category.type == input_data.type,
            )
        )
    ).scalar()
    if category_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already created such category",
        )
    category = models.Category(user_id=current_user.id, **input_data.model_dump())
    db.add(category)
    db.commit()
    return category


@router.put(
    "/{category_id}/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_v_1.Category,
)
async def create_category(
    category_id: PositiveInt,
    input_data: schemas_v_1.CategoryCreate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Update category \n
    PATH params \n
    category_id: PositiveInt \n
    JSON data \n
    `title`: str \n
    `description`: Optional[str] \n
    `type`: CategoryTypeEnum \n
    Responses: \n
    `201` CREATED \n
    `404` NOT FOUND - Returns if Category not found \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation
    """
    category = db.query(models.Category).filter(
        models.Category.id == category_id, models.Category.user_id == current_user.id
    )
    if not category.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    category.update({**input_data.model_dump()})
    category = category.one()
    return category


@router.delete("/{category_id}/")
async def delete_category(
    category_id: PositiveInt,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Delete category \n
    PATH params \n
    category_id: PositiveInt \n
    Responses: \n
    `204` NO CONTENT \n
    `404` NOT FOUND - Returns if Category not found \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation
    """
    category = db.query(models.Category).filter(
        models.Category.id == category_id, models.Category.user_id == current_user.id
    )
    if not category.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    category.delete()
    db.commit()
    return status.HTTP_204_NO_CONTENT


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.CategoryTransactions],
)
async def get_my_categories(
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my categories \n
    Responses: \n
    `200` OK
    """
    my_categories = db.query(models.Category).filter(
        models.Category.user_id == current_user.id
    )
    return paginate(my_categories)


@router.get(
    "/my/expense/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.CategoryTransactions],
)
async def get_my_expense_categories(
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my expense categories \n
    Responses: \n
    `200` OK
    """
    my_categories = db.query(models.Category).filter(
        models.Category.user_id == current_user.id,
        models.Category.type == models.CategoryTypeEnum.EXPENSE.value,
    )
    return paginate(my_categories)


@router.get(
    "/my/income/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.CategoryTransactions],
)
async def get_my_income_categories(
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my income categories \n
    Responses: \n
    `200` OK
    """
    my_categories = db.query(models.Category).filter(
        models.Category.user_id == current_user.id,
        models.Category.type == models.CategoryTypeEnum.INCOME.value,
    )
    return paginate(my_categories)


@router.get(
    "/{category_id}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas_v_1.CategoryTransactions,
)
async def get_my_category_by_id(
    category_id: PositiveInt,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my category by id \n
    PATH params \n
    `category_id`: PositiveInt \n
    Responses: \n
    `200` OK \n
    `404` NOT FOUND - Category not found
    """
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id,
            models.Category.user_id == current_user.id,
        )
        .one_or_none()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category


@router.get(
    "/transaction/filter/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.CategoryTransactions],
)
async def get_my_transactions_by_filter(
    search_type: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my categories with transactions with filter \n
    QUERY params \n
    `search_type`: str \n
    `start_date`: Optional[date] \n
    `end_date`: Optional[date] \n
    Responses: \n
    `201` CREATED \n
    `400` BAD REQUEST - Wrong filter
    """
    search_enum_check(search_type, start_date, end_date)
    categories = category_tr_filter_search(
        db, search_type, current_user.id, start_date, end_date
    )
    return paginate(categories)


@router.get(
    "/expense/transaction/filter/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.CategoryTransactions],
)
async def get_my_transactions_by_filter(
    search_type: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my expense categories with transactions with filter \n
    QUERY params \n
    `search_type`: str \n
    `start_date`: Optional[date] \n
    `end_date`: Optional[date] \n
    Responses: \n
    `201` CREATED \n
    `400` BAD REQUEST - Wrong filter
    """
    search_enum_check(search_type, start_date, end_date)
    categories = category_tr_filter_search(
        db, search_type, current_user.id, start_date, end_date, expense=True
    )
    return paginate(categories)


@router.get(
    "/income/transaction/filter/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.CategoryTransactions],
)
async def get_my_transactions_by_filter(
    search_type: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my income categories with transactions with filter \n
    QUERY params \n
    `search_type`: str \n
    `start_date`: Optional[date] \n
    `end_date`: Optional[date] \n
    Responses: \n
    `201` CREATED \n
    `400` BAD REQUEST - Wrong filter
    """
    search_enum_check(search_type, start_date, end_date)
    categories = category_tr_filter_search(
        db, search_type, current_user.id, start_date, end_date, income=True
    )
    return paginate(categories)
