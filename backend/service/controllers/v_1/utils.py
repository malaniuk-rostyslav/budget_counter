from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload, selectinload, with_loader_criteria

from db import models


def search_enum_check(search_type, start_date, end_date):
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


def transactions_filter_search(
    db, search_type, user_id, start_date, end_date, category_id
):
    if search_type.upper() == models.SearchTypeEnum.DAY.value:
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category_id == category_id,
            models.Transaction.date == date.today(),
        )
    elif search_type.upper() == models.SearchTypeEnum.WEEK.value:
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_of_week,
        )
    elif search_type.upper() == models.SearchTypeEnum.MONTH.value:
        start_of_month = date(date.today().year, date.today().month, 1)
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_of_month,
        )
    elif search_type.upper() == models.SearchTypeEnum.YEAR.value:
        start_of_year = date(date.today().year, 1, 1)
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_of_year,
        )
    elif search_type.upper() == models.SearchTypeEnum.INTERVAL.value:
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category_id == category_id,
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date,
        )
    return transactions.options(joinedload(models.Transaction.category))


def category_tr_filter_search(
    db, search_type, user_id, start_date, end_date, expense=None, income=None
):
    if search_type.upper() == models.SearchTypeEnum.DAY.value:
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(models.Category.user_id == user_id)
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
            .filter(models.Category.user_id == user_id)
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
            .filter(models.Category.user_id == user_id)
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
            .filter(models.Category.user_id == user_id)
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction, models.Transaction.date >= start_of_year
                ),
            )
        )
    elif search_type.upper() == models.SearchTypeEnum.INTERVAL.value:
        categories = (
            db.query(models.Category)
            .join(models.Transaction)
            .filter(models.Category.user_id == user_id)
            .options(
                selectinload(models.Category.transaction),
                with_loader_criteria(
                    models.Transaction,
                    models.Transaction.date >= start_date,
                    models.Transaction.date <= end_date,
                ),
            )
        )
    if expense:
        categories = categories.filter(
            models.Category.type == models.CategoryTypeEnum.EXPENSE.value
        )
    if income:
        categories = categories.filter(
            models.Category.type == models.CategoryTypeEnum.INCOME.value
        )
    return categories
