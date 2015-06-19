from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

from alppaca.util import init_logging
logger = init_logging(False)


def job_executed_event_listener(_):
    logger.info("Successfully completed credentials refresh")


def job_failed_event_listener(event):
    logger.error("Failed to refresh credentials: {0}".format(event.exception))


def job_missed_event_listener(_):
    logger.warn('Credentials refresh was not executed in time!')


def configure_scheduler(func, repeat=55):
    task_scheduler = BackgroundScheduler()
    trigger = IntervalTrigger(minutes=repeat)
    task_scheduler.add_job(func=func, trigger=trigger)
    task_scheduler.add_listener(job_executed_event_listener, EVENT_JOB_EXECUTED)
    task_scheduler.add_listener(job_failed_event_listener, EVENT_JOB_ERROR)
    task_scheduler.add_listener(job_missed_event_listener, EVENT_JOB_MISSED)
    return task_scheduler
