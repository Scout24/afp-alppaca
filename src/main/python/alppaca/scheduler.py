import datetime
from random import uniform

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

from alppaca.util import init_logging, convert_rfc3339_to_datetime, extract_min_expiration, total_seconds
from alppaca.delaytrigger import DelayTrigger


logger = init_logging(False)


class Scheduler(object):
    
    def __init__(self, credentials, ims_interface):
        self.credentials = credentials
        
        self.ims_interface = ims_interface
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self.job_executed_event_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.job_failed_event_listener, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self.job_missed_event_listener, EVENT_JOB_MISSED)

    def job_executed_event_listener(_):
        logger.info("Successfully completed credentials refresh")

    def job_failed_event_listener(event):
        logger.error("Failed to refresh credentials: {0}".format(event.exception))
    
    def job_missed_event_listener(_):
        logger.warn('Credentials refresh was not executed in time!')

    def refresh_credentials(self):
        self.credentials = self.ims_interface.get_credentials_for_all_roles()
        expiration = convert_rfc3339_to_datetime(extract_min_expiration(self.credentials))
        self.build_trigger(expiration)
    
    def build_trigger(self, expiration):
        refresh_delta = total_seconds(expiration - datetime.datetime.utcnow())
        refresh_delta = int(round(refresh_delta / uniform(1.2, 2), 0))
        if refresh_delta < 0:
            #TODO: log this
            refresh_delta = 0
    
        self.scheduler.add_job(func=self.refresh_credentials, trigger=DelayTrigger(refresh_delta))

