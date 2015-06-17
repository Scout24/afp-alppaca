from bottle import Bottle

from alppaca import IMSInterface

bottle_app = Bottle(__name__)
path = '/latest/meta-data/iam/security-credentials/'
local_host = '127.0.0.1'
local_port = 5000
ims_host = 'localhost'


roles = []
credentials = {}


@bottle_app.route(path)
def get_roles():
    return "\n".join(roles)


@bottle_app.route(path+'<role>')
def get_credentials(role):
    pass
