from db import models
from workers.celery_app import SqlAlchemyTask, celery_app


@celery_app.task(acks_late=True, base=SqlAlchemyTask, bind=True)
def update_currency_in_transactions(
    self,
    currency_to_update,
    currency_to_replace,
    cross_course,
    start_date,
    end_date,
    user_id,
):
    transactions = self.session.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.currency == currency_to_replace,
        models.Transaction.date.between(start_date, end_date),
    )
    for tr in transactions:
        tr.amount = float(tr.amount) * cross_course
        tr.currency = currency_to_update
        self.session.commit()
