from util import init_logging
from bottle import Bottle

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED


from alppaca import IMSInterface
from alppaca.compat import OrderedDict

bottle_app = Bottle(__name__)
path = '/latest/meta-data/iam/security-credentials/'
local_host = '127.0.0.1'
local_port = 5000
ims_host = 'localhost'
ims_port = '8080'

credentials = OrderedDict()

task_scheduler = BackgroundScheduler()
task_scheduler.start()

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


def job_executed_event_listener(_):
    logger.debug("Successfully completed credentials refresh")


def job_failed_event_listener(event):
    logger.error("Failed to refresh credentials: {0}".format(event.exception))


def job_missed_event_listener(_):
    logger.warn('Credentials refresh was not executed in time!')


def init_roles():
    logger.info("Initializing local credentials cache")
    refresh_roles()


def run_scheduler_and_webserver():
    try:
        trigger = IntervalTrigger(minutes=20)
        task_scheduler.add_job(func=refresh_roles, trigger=trigger)
        task_scheduler.add_listener(job_executed_event_listener, EVENT_JOB_EXECUTED)
        task_scheduler.add_listener(job_failed_event_listener, EVENT_JOB_ERROR)
        task_scheduler.add_listener(job_missed_event_listener, EVENT_JOB_MISSED)

#        init_roles()
#        app.run('127.0.0.1', 5000, threaded=True)

    except Exception, e:
        print e

if __name__ == '__main__':

    run_scheduler_and_webserver()