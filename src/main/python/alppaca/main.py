from ims_interface import IMSInterface
from scheduler import Scheduler
from webapp import WebApp
from util import load_config
from compat import OrderedDict


def run_scheduler_and_webserver(config_file_path):
    try:
        config = load_config(config_file_path)
        # Credentials is a shared object that connects the scheduler and the
        # bottle_app. The scheduler writes into it and the bottle_app reads
        # from it.
        credentials = OrderedDict()
        # initialize the credentials provider
        ims_host_port = '%s:%s' % (config['ims_host'], config['ims_port'])
        ims_protocol = config.get('ims_protocol', 'https')
        ims_interface = IMSInterface(ims_host_port, ims_protocol=ims_protocol)
        Scheduler(credentials, ims_interface).refresh_credentials()
        # initialize and run the web app
        webapp = WebApp(credentials)
        webapp.run(host='127.0.0.1', port=5000)
    except Exception, e:
        print e

if __name__ == '__main__':
    configpath = 'src/main/python/resources/example_config.yaml'
    run_scheduler_and_webserver(configpath)
