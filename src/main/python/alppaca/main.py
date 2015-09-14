import sys
from ims_interface import IMSInterface
from scheduler import Scheduler
from webapp import WebApp
from util import load_config, setup_logging
from compat import OrderedDict


def run_scheduler_and_webserver(config_file_path):
    try:
        config = load_config(config_file_path)
    except Exception:
        print >>sys.stderr, "Could not load configuration from '{0}'".format(
            config_file_path)
        raise
    logging_config = None
    try:
        logging_config = config.get('logging_handler')
        logger = setup_logging(logging_config)
    except Exception:
        print >>sys.stderr, "Could not setup logging with config '{0}'".format(
            logging_config)
        raise
    try:
        # Credentials is a shared object that connects the scheduler and the
        # bottle_app. The scheduler writes into it and the bottle_app reads
        # from it.
        credentials = OrderedDict()
        # initialize the credentials provider
        ims_host_port = '%s:%s' % (config['ims_host'], config['ims_port'])
        ims_protocol = config.get('ims_protocol', 'https')
        ims_interface = IMSInterface(ims_host_port, ims_protocol=ims_protocol)
        bind_ip = config.get('bind_ip', '127.0.0.1')
        bind_port = config.get('bind_port', '5000')
        Scheduler(credentials, ims_interface).refresh_credentials()
        # initialize and run the web app
        webapp = WebApp(credentials)
        webapp.run(host=bind_ip, port=bind_port)
    except Exception:
        logger.exception("Cannot start Alppaca")

if __name__ == '__main__':
    configpath = 'src/main/python/resources/example_config.yaml'
    run_scheduler_and_webserver(configpath)
