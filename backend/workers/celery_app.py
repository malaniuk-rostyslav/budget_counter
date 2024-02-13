import os
from abc import ABC

from celery import Celery, Task
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from service.core import settings

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend="rpc://",
)

celery_app.conf.broker_transport_options = {
    "sentinel_kwargs": {"password": os.getenv("RABBITMQ_PASSWORD")}
}


class SqlAlchemyTask(Task, ABC):
    """An abstract Celery Task that ensures that the connection the
    database is closed on task completion"""

    abstract = True
    _session = None

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if self._session is not None:
            self._session.remove()

    def _get_engine_session(self):
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        session = scoped_session(
            sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
        )
        return session

    @property
    def session(self):
        if self._session is None:
            self._session = self._get_engine_session()
        return self._session


celery_app.conf.task_routes = {"workers.celery_tasks.test_celery": "main-queue"}
