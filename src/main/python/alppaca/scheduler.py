import datetime
import json
from random import uniform
from time import strptime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import pytz

from util import init_logging
from delaytrigger import DelayTrigger

logger = init_logging(False)


class Scheduler(object):
    """ Scheduler for refreshing credentials.

        By default it will fetch the credentials and then schedule itself to
        update them based on the expiration date. Some randomness is involved
        to avoid collisions. In case of failure to fetch credentials a back-off
        and safety behaviour is initiated.

        It is based on the apscheduler package.

    """

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

    def do_backoff(self):
        """ Perform back-off and safety. """
        if self.backoff is None:
            logger.info("Initialize back-off and safety behaviour")
            self.backoff = backoff_refresh_generator()
        refresh_delta = self.backoff.next()
        self.build_trigger(refresh_delta)

    def refresh_credentials(self):
        """ Refresh credentials and schedule next refresh."""
        logger.info("about to fetch credentials")

        cached_credentials = self.ims_interface.get_credentials_for_all_roles()

        if not cached_credentials:
            logger.info("No credentials found!")
            self.do_backoff()
        else:
            self.credentials.update(cached_credentials)
            logger.info("Got credentials: {0}".format(self.credentials))
            refresh_delta = self.extract_refresh_delta()
            if refresh_delta < 0:
                logger.warn("Expiration date is in the past, enter backoff.")
                self.do_backoff()
            else:
                if self.backoff is not None:
                    self.backoff = None
                    logger.info("Exit backoff state.")
                refresh_delta = self.sample_new_refresh_delta(refresh_delta)
                self.build_trigger(refresh_delta)

    def extract_refresh_delta(self):
        """ Return shortest expiration time in seconds. """
        expiration = convert_rfc3339_to_datetime(extract_min_expiration(self.credentials))
        logger.info("Extracted expiration: {0}".format(expiration))
        refresh_delta = total_seconds(expiration - datetime.datetime.now(tz=pytz.utc))
        return refresh_delta

    def sample_new_refresh_delta(self, refresh_delta):
        """ Sample a new refresh delta. """
        refresh_delta = int(uniform(refresh_delta * .5, refresh_delta * .9))
        return refresh_delta

    def build_trigger(self, refresh_delta):
        """ Actually add the trigger to the apscheduler. """
        logger.info("Setting up trigger to fire in {0} seconds".format(refresh_delta))
        self.scheduler.add_job(func=self.refresh_credentials, trigger=DelayTrigger(refresh_delta))


def backoff_refresh_generator():
    """ Generate refresh deltas when in back-off and safety mode. """
    count = 0
    while True:
        yield count if count < 10 else 10
        count += 1


def convert_rfc3339_to_datetime(timestamp):
    """ Convert AWS timestamp to datetime object. """
    return datetime.datetime(*strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")[0:6], tzinfo=pytz.utc)


def extract_min_expiration(credentials):
    """ The smallest expiration date of all the available credentials. """
    return min([json.loads(value)['Expiration']
                for value in credentials.values()])


def total_seconds(timedelta):
    """ Convert timedelta to seconds as an integer. """
    return (timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 10**6) / 10**6
