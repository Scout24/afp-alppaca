from ims_interface import IMSInterface
from scheduler import configure_scheduler
from webapp import WebApp

from alppaca import util


def run_scheduler_and_webserver(config_file_path):
    try:
        config = util.load_config(config_file_path)
        # initialize the credentials provider
        credentials_provider = IMSInterface('{0}:{1}'.format(config['ims_host'], config['ims_port']))
        scheduler = configure_scheduler()
        # initialize and run the web app
        bottle_app = WebApp(credentials_provider, scheduler)
        bottle_app.run(host='127.0.0.1', port=5000)
    except Exception, e:
        print e

if __name__ == '__main__':
    run_scheduler_and_webserver()
