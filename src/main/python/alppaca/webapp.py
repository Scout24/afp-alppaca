from flask import Flask

from alppaca import IMSInterface

flask_app = Flask(__name__)
path = '/latest/meta-data/iam/security-credentials/'
local_host = '127.0.0.1'
local_port = 5000
ims_host = 'localhost'


credentials = {}

@flask_app.route(path, methods=['GET'])
def get_roles():
    return "\n".join(sorted(credentials.keys()))

@flask_app.route(path+'<string:role>', methods=['GET'])
def get_credentials(role):
    pass
