from ims_interface import IMSInterface
from scheduler import configure_scheduler
from webapp import WebApp

local_host = '127.0.0.1'
local_port = 5000
ims_host = 'localhost'
ims_port = '8080'


def run_scheduler_and_webserver():
    try:
        # initialize the credentials provider
        credentials_provider = IMSInterface('{0}:{1}'.format(ims_host, ims_port))
        scheduler = configure_scheduler()
        # initialize and run the webapp
        bottle_app = WebApp(credentials_provider, scheduler)
        bottle_app.run(host=local_host, port=local_port)
    except Exception, e:
        print e

if __name__ == '__main__':
    run_scheduler_and_webserver()
