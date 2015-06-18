from util import init_logging
from bottle import Bottle

from alppaca import IMSInterface
from alppaca.scheduler import configure_scheduler

local_host = '127.0.0.1'
local_port = 5000
ims_host = 'localhost'
ims_port = '8080'


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


def run_scheduler_and_webserver():
    try:
        # initialize the credentials provider
        credentials_provider = IMSInterface('{0}:{1}'.format(ims_host, ims_port))
        # initialize the webapp
        bottle_app = WebApp(credentials_provider)
        # setup the scheduler
        task_scheduler = configure_scheduler(bottle_app.refresh_credentials, repeat=1)

        # run them both
        task_scheduler.start()
        bottle_app.run(host=local_host, port=local_port)
    except Exception, e:
        print e

if __name__ == '__main__':
    run_scheduler_and_webserver()
