from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import UJSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import PositiveInt
from sqlalchemy import and_, exists
from sqlalchemy.orm import selectinload, with_loader_criteria

from db import models
from db.session import DBSession
from service.core.dependencies import get_current_user, get_db
from service.schemas import v_1 as schemas_v_1

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
    search_enum_values = [st.value for st in models.SearchTypeEnum]
    if search_type.upper() not in search_enum_values or (
        search_type.upper() == models.SearchTypeEnum.INTERVAL.value
        and (
            not start_date
            or not end_date
            or start_date > end_date
            or end_date > date.today()
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong filter"
        )
    if search_type.upper() == models.SearchTypeEnum.DAY.value:
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(models.Category.user_id == current_user.id)
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date == date.today()
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.WEEK.value:
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(models.Category.user_id == current_user.id)
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_week
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.MONTH.value:
        start_of_month = date(date.today().year, date.today().month, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(models.Category.user_id == current_user.id)
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_month
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.YEAR.value:
        start_of_year = date(date.today().year, 1, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(models.Category.user_id == current_user.id)
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_year
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.INTERVAL.value:
        start_of_year = date(date.today().year, 1, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(models.Category.user_id == current_user.id)
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction,
                    models.Transaction.date >= start_date,
                    models.Transaction.date <= end_date,
                ),
            )
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
    search_enum_values = [st.value for st in models.SearchTypeEnum]
    if search_type.upper() not in search_enum_values or (
        search_type.upper() == models.SearchTypeEnum.INTERVAL.value
        and (
            not start_date
            or not end_date
            or start_date > end_date
            or end_date > date.today()
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong filter"
        )
    if search_type.upper() == models.SearchTypeEnum.DAY.value:
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.EXPENSE.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date == date.today()
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.WEEK.value:
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.EXPENSE.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_week
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.MONTH.value:
        start_of_month = date(date.today().year, date.today().month, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.EXPENSE.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_month
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.YEAR.value:
        start_of_year = date(date.today().year, 1, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.EXPENSE.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_year
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.INTERVAL.value:
        start_of_year = date(date.today().year, 1, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.EXPENSE.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction,
                    models.Transaction.date >= start_date,
                    models.Transaction.date <= end_date,
                ),
            )
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
    search_enum_values = [st.value for st in models.SearchTypeEnum]
    if search_type.upper() not in search_enum_values or (
        search_type.upper() == models.SearchTypeEnum.INTERVAL.value
        and (
            not start_date
            or not end_date
            or start_date > end_date
            or end_date > date.today()
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong filter"
        )
    if search_type.upper() == models.SearchTypeEnum.DAY.value:
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.INCOME.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date == date.today()
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.WEEK.value:
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.INCOME.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_week
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.MONTH.value:
        start_of_month = date(date.today().year, date.today().month, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.INCOME.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_month
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.YEAR.value:
        start_of_year = date(date.today().year, 1, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.INCOME.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_year
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.INTERVAL.value:
        start_of_year = date(date.today().year, 1, 1)
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(
                models.Category.user_id == current_user.id,
                models.Category.type == models.CategoryTypeEnum.INCOME.value,
            )
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction,
                    models.Transaction.date >= start_date,
                    models.Transaction.date <= end_date,
                ),
            )
        )
    return paginate(categories)
