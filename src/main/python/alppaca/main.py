import datetime

from ims_interface import IMSInterface
import pytz
from scheduler import Scheduler
from webapp import WebApp
from alppaca import util


def run_scheduler_and_webserver(config_file_path):
    try:
        config = util.load_config(config_file_path)
        credentials = {}
        # initialize the credentials provider
        ims_interface = IMSInterface('{0}:{1}'.format(config['ims_host'], config['ims_port']))
        Scheduler(credentials, ims_interface).build_trigger(datetime.datetime.now(tz=pytz.utc))
        # initialize and run the web app
        bottle_app = WebApp(credentials)
        bottle_app.run(host='127.0.0.1', port=5000)
    except Exception, e:
        print e

if __name__ == '__main__':
    run_scheduler_and_webserver('../resources/example_config.yaml')
