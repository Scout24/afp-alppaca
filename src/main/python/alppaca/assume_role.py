from __future__ import print_function, absolute_import, unicode_literals, division

from alppaca import NoCredentialsFoundException
from alppaca.compat import OrderedDict
import json
from boto.sts import connect_to_region
import socket


class AssumedRoleCredentialsProvider():
    def __init__(self, credentials_provider, role_to_assume, aws_proxy_host=None, aws_proxy_port=None):
        self.credentials_provider = credentials_provider
        self.role_to_assume = role_to_assume
        self.aws_proxy_host = aws_proxy_host
        self.aws_proxy_port = aws_proxy_port

    def get_credentials_for_all_roles(self):
        original_credentials = self.credentials_provider.get_credentials_for_all_roles()
        if not original_credentials:
            raise NoCredentialsFoundException("Got not get credentials from: " + str(self.credentials_provider))

        for role in original_credentials:
            access_key, secret_key, token = self.parse_credentials_json(original_credentials[role])
            return self.get_assume_role_credentials(access_key, secret_key, token)

    @staticmethod
    def parse_credentials_json(credentials_json):
        credentials_dict = json.loads(credentials_json)
        return credentials_dict['AccessKeyId'], credentials_dict['SecretAccessKey'], credentials_dict['Token']

    def get_assume_role_credentials(self, access_key, secret_key, token):
        conn = connect_to_region('eu-central-1',
                                          aws_access_key_id=access_key,
                                          aws_secret_access_key=secret_key,
                                          security_token=token,
                                          proxy=self.aws_proxy_host,
                                          proxy_port=self.aws_proxy_port
                                          )
        response = conn.assume_role(role_arn=self.role_to_assume, role_session_name=self.get_session_name())

        results = OrderedDict()
        results[self.get_role_name()] = self.create_credentials_json(response)

        return results

    @staticmethod
    def get_session_name():
        return 'alppaca-session-of-' + socket.gethostname()

    def get_role_name(self):
        return self.role_to_assume.split('/')[1]

    @staticmethod
    def create_credentials_json(assume_role_response):
        credentials = assume_role_response.credentials
        credentials_dict = {
            'AccessKeyId': credentials.access_key,
            'SecretAccessKey': credentials.secret_key,
            'Token': credentials.session_token,
            'Expiration': credentials.expiration
        }
        return json.dumps(credentials_dict)
