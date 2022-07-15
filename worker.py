from celery import Celery 
from celery.schedules import crontab

import os
from settings import Settings
from db import engine

settings = Settings()

celery = Celery(broker=f"{settings.REDIS_URL}")
logger = celery.log.get_default_logger()


@celery.task
def clear_stats():
    """
    Delete files from stats folder
    """
    logger.info("Start task delete stats")
    os.system("rm stats/*")
    logger.info("End task delete stats")
    return True 


@celery.task
def delete_blacklist():
    """
    Delete all tokens from blacklist
    """
    logger.info("Start delete tokens from blacklist")
    with engine.connect().execution_options(autocommit=True) as conn:
        conn.exec_driver_sql("DELETE FROM blacklist")
    logger.info("Done delete tokens from blacklist")


celery.conf.beat_schedule = {
    "every-1-minute": {
        "task": "worker.clear_stats",
        "schedule": crontab(minute="*/1"),
    },
    "every-2-minute": {
        "task": "worker.delete_blacklist",
        "schedule": crontab(minute=0, hour=0),
    },
}
