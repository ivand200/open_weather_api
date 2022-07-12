from celery import Celery 
from celery.schedules import crontab

import os
from settings import Settings

settings = Settings()

celery = Celery(broker=f"{settings.REDIS_URL}")
logger = celery.log.get_default_logger()


@celery.task
def test():
    """
    Delete files from stats folder
    """
    logger.info("Start task delete stats")
    os.system("rm stats/*")
    logger.info("End task delete stats")
    return True 


celery.conf.beat_schedule = {
    "every-1-minute": {
        "task": "worker.test",
        "schedule": crontab(minute="*/1"),
    }
}
