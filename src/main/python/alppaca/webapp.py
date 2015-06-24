import json
from datetime import datetime
from random import uniform
from time import strptime

from alppaca.afterxminstrigger import AfterXMinsTrigger
from bottle import Bottle
import pytz
from util import init_logging

logger = init_logging(False)


class WebApp(Bottle):

    PATH = '/latest/meta-data/iam/security-credentials/'

    def __init__(self, credentials_provider, task_scheduler):
        super(WebApp, self).__init__()
        self.credentials_provider = credentials_provider
        self.task_scheduler = task_scheduler
        logger.info("Initializing local credentials cache")
        self.credentials = None
        self.refresh_credentials()

        self.route(self.PATH, callback=self.get_roles)
        self.route(self.PATH + '<role>', callback=self.get_credentials)

    def refresh_credentials(self):
        try:
            self.credentials = self.credentials_provider.get_credentials_for_all_roles()
            min_expiration = convert_rfc3339_to_datetime(extract_min_expiration(self.credentials))
            self.build_trigger(min_expiration)
        except:
            pass

    def build_trigger(self, min_expiration):
        refresh_delta = min_expiration - datetime.utcnow()
        refresh_delta -= (refresh_delta / uniform(1, 2))

        self.task_scheduler.add_job(func=self.refresh_credentials, trigger=AfterXMinsTrigger(refresh_delta))

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
