import asyncio

from sqlalchemy.orm import Session

from db import manager, models
from db.session import DBSession
from service.core import settings


async def init_db(db: Session) -> None:
    """Tables should be created with Alembic migrations"""
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    user = (
        db.query(models.User)
        .filter(models.User.email == settings.FIRST_SUPERUSER)
        .scalar()
    )
    if user:
        return

    user_data = {
        "email": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
        "birthday": settings.FIRST_SUPERUSER_BIRTHDAY,
        "is_superuser": True,
    }
    await manager.create_user(db, user_data=user_data)
    db.commit()


async def main() -> None:
    with DBSession() as session:
        await init_db(session)
    return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
