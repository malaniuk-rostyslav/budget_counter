import asyncio
import logging

from sqlalchemy_utils import create_database, database_exists
from tenacity import (after_log, before_log, retry, stop_after_attempt,
                      wait_fixed)

from service.core import settings

DB_URI = {settings.SQLALCHEMY_DATABASE_URI, settings.CELERY_SQLALCHEMY_DATABASE_URI}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init_database() -> None:
    for db_uri in DB_URI:
        if not database_exists(db_uri):
            logging.warning(f"{db_uri} doesn't exist")
            create_database(db_uri)
            logging.info(f"{db_uri} has been created")
        logging.info(f"{db_uri} already exist!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())
