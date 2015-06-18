from util import init_logging
from bottle import Bottle

from alppaca import IMSInterface
from alppaca.compat import OrderedDict
from alppaca.scheduler import configure_scheduler

bottle_app = Bottle(__name__)
path = '/latest/meta-data/iam/security-credentials/'
local_host = '127.0.0.1'
local_port = 5000
ims_host = 'localhost'
ims_port = '8080'

credentials = OrderedDict()

logger = init_logging(False)

credentials_provider = IMSInterface('{0}:{1}'.format(ims_host, ims_port))


@bottle_app.route(path)
def get_roles():
    return "\n".join(credentials.keys())


@bottle_app.route(path+'<role>')
def get_credentials(role):
    try:
        return credentials[role]
    except KeyError:
        return ""


def refresh_roles():
    global credentials
    credentials = credentials_provider.get_credentials_for_all_roles()


def init_roles():
    logger.info("Initializing local credentials cache")
    refresh_roles()


def run_scheduler_and_webserver():
    try:
        init_roles()
        task_scheduler = configure_scheduler(refresh_roles, repeat=1)
        task_scheduler.start()
        bottle_app.run(host=local_host, port=local_port)
    except Exception, e:
        print e

if __name__ == '__main__':
    run_scheduler_and_webserver()
