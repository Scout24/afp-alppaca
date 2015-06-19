import json

from bottle import Bottle

from util import init_logging

logger = init_logging(False)


class WebApp(Bottle):

    PATH = '/latest/meta-data/iam/security-credentials/'

    def __init__(self, credentials_provider):
        super(WebApp, self).__init__()
        self.credentials_provider = credentials_provider
        logger.info("Initializing local credentials cache")
        self.refresh_credentials()
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

def convert_to_datetime():
    pass

def extract_min_expiration(credentials):
    return min([json.loads(value)['Expiration']
                for value in credentials.values()])
