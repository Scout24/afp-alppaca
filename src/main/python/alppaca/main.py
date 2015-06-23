from ims_interface import IMSInterface
from scheduler import configure_scheduler
from webapp import WebApp


def run_scheduler_and_webserver(ims_host, ims_port):
    try:
        # initialize the credentials provider
        credentials_provider = IMSInterface('{0}:{1}'.format(ims_host, ims_port))
        scheduler = configure_scheduler()
        # initialize and run the webapp
        bottle_app = WebApp(credentials_provider, scheduler)
        bottle_app.run(host='127.0.0.1', port=5000)
    except Exception, e:
        print e

if __name__ == '__main__':
    run_scheduler_and_webserver()
