import json
from datetime import datetime
from time import strptime

from apscheduler.triggers.date import DateTrigger
from bottle import Bottle
import pytz

from scheduler import configure_scheduler
from util import init_logging


logger = init_logging(False)


class WebApp(Bottle):

    PATH = '/latest/meta-data/iam/security-credentials/'

    def __init__(self, credentials_provider):
        super(WebApp, self).__init__()
        self.credentials_provider = credentials_provider
        logger.info("Initializing local credentials cache")
        self.credentials = None
        self.refresh_credentials()

        next_refresh = convert_rfc3339_to_datetime(extract_min_expiration(self.credentials))
        trigger = DateTrigger(next_refresh)
        
        task_scheduler = configure_scheduler()
        task_scheduler.add_job(func=self.refresh_credentials, trigger=trigger)
        
        self.route(self.PATH, callback=self.get_roles)
        self.route(self.PATH + '<role>', callback=self.get_credentials)

    def refresh_credentials(self):
        self.credentials = self.credentials_provider.get_credentials_for_all_roles()

    def get_roles(self):
        return "\n".join(self.credentials.keys())

    def get_credentials(self, role):
        try:
            return self.credentials[role]
        except KeyError:
            return ""


def convert_rfc3339_to_datetime(timestamp):
    return datetime(
        *strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")[0:6], tzinfo=pytz.utc)


def extract_min_expiration(credentials):
    return min([json.loads(value)['Expiration']
                for value in credentials.values()])
