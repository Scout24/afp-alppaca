from bottle import Bottle

from util import init_logging

logger = init_logging(False)


class WebApp(Bottle):

    PATH = '/latest/meta-data/iam/security-credentials/'

    def __init__(self, credentials):
        super(WebApp, self).__init__()
        self.credentials = credentials

        self.route(self.PATH, callback=self.get_roles)
        self.route(self.PATH + '<role>', callback=self.get_credentials)

    def get_roles(self):
        return "\n".join(self.credentials.keys())

    def get_credentials(self, role):
        try:
            return self.credentials[role]
        except KeyError:
            return ""
