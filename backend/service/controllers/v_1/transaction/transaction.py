from datetime import date, timedelta
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

router = APIRouter()


@router.post(
    "/{category_id}/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_v_1.Transaction,
)
async def create_transaction(
    category_id: PositiveInt,
    input_data: schemas_v_1.TransactionCreate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Create transaction \n
    PATH params \n
    `category_id`: PositiveInt \n
    JSON data \n
    `amount`: float \n
    `date`: date \n
    `note`: Optional[str] \n
    Responses: \n
    `201` CREATED \n
    `404` NOT FOUND - Category not found \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation
    """
    category_exists = db.query(
        exists().where(
            and_(
                models.Category.id == category_id,
                models.Category.user_id == current_user.id,
            )
        )
    ).scalar()
    if not category_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    us_currency = (
        db.query(models.UserSettings.default_currency)
        .filter(models.UserSettings.user_id == current_user.id)
        .scalar()
    )
    transaction = models.Transaction(
        user_id=current_user.id,
        category_id=category_id,
        currency=us_currency,
        **input_data.model_dump()
    )
    db.add(transaction)
    db.commit()
    return transaction


@router.put(
    "/{transaction_id}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas_v_1.Transaction,
)
async def update_transaction(
    transaction_id: PositiveInt,
    input_data: schemas_v_1.TransactionCreate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Update transaction \n
    PATH params \n
    `category_id`: PositiveInt \n
    `transaction_id`: PositivrInt \n
    JSON data \n
    `amount`: float \n
    `date`: date \n
    `note`: Optional[str] \n
    Responses: \n
    `201` CREATED \n
    `404` NOT FOUND - Category or transaction not found \n
    `422` UNPROCESSABLE_ENTITY - Failed field validation
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id,
    )
    if not transaction.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    transaction.update({**input_data.model_dump()})
    db.commit()
    transaction = transaction.one()
    return transaction


@router.delete("/{transaction_id}/")
async def update_transaction(
    transaction_id: PositiveInt,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Delete transaction \n
    PATH params \n
    `transaction_id`: PositivrInt \n
    Responses: \n
    `204` NO CONTENT \n
    `404` NOT FOUND - Category not found \n
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id,
    )
    if not transaction.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    transaction.delete()
    db.commit()
    return status.HTTP_204_NO_CONTENT


@router.get(
    "/{transaction_id}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas_v_1.Transaction,
)
async def get_transaction_by_id(
    transaction_id: PositiveInt,
    input_data: schemas_v_1.TransactionCreate,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get transaction by id \n
    PATH params \n
    `transaction_id`: PositivrInt \n
    Responses: \n
    `201` CREATED \n
    `404` NOT FOUND - Category or transaction not found \n
    """
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.user_id == current_user.id,
        )
        .one_or_none()
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction


@router.get(
    "/category/{category_id}/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.Transaction],
)
async def get_my_transactions_by_category(
    category_id: PositiveInt,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my transactions by category \n
    PATH params \n
    `category_id`: PositiveInt \n
    Responses: \n
    `201` CREATED \n
    `404` NOT FOUND - Category not found
    """
    category_exists = db.query(
        exists().where(
            and_(
                models.Category.id == category_id,
                models.Category.user_id == current_user.id,
            )
        )
    ).scalar()
    if not category_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.category_id == category_id,
    )
    return paginate(transactions)


@router.get(
    "/category/{category_id}/filter/",
    status_code=status.HTTP_200_OK,
    response_model=Page[schemas_v_1.Transaction],
)
async def get_my_transactions_by_filter(
    category_id: PositiveInt,
    search_type: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> UJSONResponse:
    """
    Get my transactions by category with filter \n
    QUERY params \n
    `search_type`: str \n
    `start_date`: Optional[date] \n
    `end_date`: Optional[date] \n
    PATH params \n
    `category_id`: PositiveInt \n
    Responses: \n
    `201` CREATED \n
    `400` BAD REQUEST - Wrong filter \n
    `404` NOT FOUND - Category not found
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
    category_exists = db.query(
        exists().where(
            and_(
                models.Category.id == category_id,
                models.Category.user_id == current_user.id,
            )
        )
    ).scalar()
    if not category_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    if search_type.upper() == models.SearchTypeEnum.DAY.value:
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.category_id == category_id,
            models.Transaction.date == date.today(),
        )
    elif search_type.upper() == models.SearchTypeEnum.WEEK.value:
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_of_week,
        )
    elif search_type.upper() == models.SearchTypeEnum.MONTH.value:
        start_of_month = date(date.today().year, date.today().month, 1)
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_of_month,
        )
    elif search_type.upper() == models.SearchTypeEnum.YEAR.value:
        start_of_year = date(date.today().year, 1, 1)
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_of_year,
        )
    elif search_type.upper() == models.SearchTypeEnum.INTERVAL.value:
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date,
        )
    return paginate(transactions)
