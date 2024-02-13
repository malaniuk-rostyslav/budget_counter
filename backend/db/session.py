from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from service.core import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False,
)
DBSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
