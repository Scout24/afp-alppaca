import datetime
from random import uniform

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from alppaca.util import init_logging, convert_rfc3339_to_datetime, extract_min_expiration, total_seconds
from alppaca.delaytrigger import DelayTrigger
import pytz

logger = init_logging(False)


def backoff_refresh_generator():
    count = 0
    while True:
        yield count if count < 10 else 10
        count += 1


class Scheduler(object):

    def __init__(self, credentials, ims_interface):
        self.credentials = credentials

        self.ims_interface = ims_interface
        self.backoff = None
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self.job_executed_event_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.job_failed_event_listener, EVENT_JOB_ERROR)
        self.scheduler.start()

    def job_executed_event_listener(self, event):
        logger.info("Successfully completed credentials refresh")

    def job_failed_event_listener(self, event):
        logger.error("Failed to refresh credentials: {0}".format(event.exception))

    def refresh_credentials(self):
        logger.info("about to fetch credentials")

        cached_credentials = self.ims_interface.get_credentials_for_all_roles()

        if not cached_credentials:
            logger.info("No credentials found!")
            logger.info("Initialize back-off and safety behaviour")
            if self.backoff is None:
                self.backoff = backoff_refresh_generator()
            refresh_delta = self.backoff.next()
            self.build_trigger(refresh_delta)

        else:
            if self.backoff is not None:
                self.backoff = None
            logger.info("Got credentials: {0}".format(self.credentials))
            self.credentials.update(cached_credentials)
            expiration = convert_rfc3339_to_datetime(extract_min_expiration(cached_credentials))
            logger.info("Calculated expiration: {0}".format(expiration))
            refresh_delta = self.determine_refresh_delta(expiration)
            self.build_trigger(refresh_delta)

    def determine_refresh_delta(self, expiration):
        refresh_delta = total_seconds(expiration - datetime.datetime.now(tz=pytz.utc))
        if refresh_delta < 0:
            logger.warn("Expiration date is in the past, triggering now!")
            refresh_delta = 0
        else:
            refresh_delta = int(uniform(refresh_delta * .5, refresh_delta * .9))
        return refresh_delta

    def build_trigger(self, refresh_delta):
        logger.info("Setting up trigger to fire in {0} seconds".format(refresh_delta))
        self.scheduler.add_job(func=self.refresh_credentials, trigger=DelayTrigger(refresh_delta))

