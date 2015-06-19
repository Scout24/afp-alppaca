from ims_interface import IMSInterface
from webapp import WebApp

local_host = '127.0.0.1'
local_port = 5000
ims_host = 'localhost'
ims_port = '8080'


def run_scheduler_and_webserver():
    try:
        # initialize the credentials provider
        credentials_provider = IMSInterface('{0}:{1}'.format(ims_host, ims_port))
        # initialize and run the webapp
        bottle_app = WebApp(credentials_provider)
        bottle_app.run(host=local_host, port=local_port)
    except Exception, e:
        print e

if __name__ == '__main__':
    run_scheduler_and_webserver()
