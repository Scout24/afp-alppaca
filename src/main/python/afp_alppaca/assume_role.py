from __future__ import print_function, absolute_import, unicode_literals, division

import json
import logging
import socket

from afp_alppaca import NoCredentialsFoundException
from afp_alppaca.compat import OrderedDict

from boto.sts import connect_to_region


class AssumedRoleCredentialsProvider(object):
    def __init__(self, credentials_provider, role_to_assume, aws_proxy_host=None, aws_proxy_port=None, aws_region=None):
        self.credentials_provider = credentials_provider
        self.role_to_assume = role_to_assume
        self.aws_proxy_host = aws_proxy_host
        self.aws_proxy_port = aws_proxy_port
        self.logger = logging.getLogger(__name__)
        self.region = aws_region or "eu-central-1"

    def get_credentials_for_all_roles(self):
        self.logger.debug("Getting credentials for all roles...")
        original_credentials = self.credentials_provider.get_credentials_for_all_roles()
        if not original_credentials:
            raise NoCredentialsFoundException("Got no credentials from: " + str(self.credentials_provider))

        for role in original_credentials:
            self.logger.debug("Got credentials for role '%s':", role)
            access_key, secret_key, token = self.parse_credentials_json(original_credentials[role])
            self.logger.debug("Access Key: %s", access_key)
            self.logger.debug("Secret Key (partial): %s...", secret_key[:10])
            self.logger.debug("Token (partial): %s...", token[:10])
            return self.get_credentials_for_assumed_role(access_key, secret_key, token)

    @staticmethod
    def parse_credentials_json(credentials_json):
        credentials_dict = json.loads(credentials_json)
        return credentials_dict['AccessKeyId'], credentials_dict['SecretAccessKey'], credentials_dict['Token']

    def get_credentials_for_assumed_role(self, access_key, secret_key, token):
        results = OrderedDict()
        self.logger.debug("Connecting to AWS region %s ...", self.region)
        try:
            conn = connect_to_region(self.region,
                                     aws_access_key_id=access_key,
                                     aws_secret_access_key=secret_key,
                                     security_token=token,
                                     proxy=self.aws_proxy_host,
                                     proxy_port=self.aws_proxy_port
                                     )
            try:
                response = conn.assume_role(role_arn=self.role_to_assume, role_session_name=self.get_session_name())
                self.logger.info("Successfully got credentials for role: %s", self.role_to_assume)
            finally:
                conn.close()
            results[self.get_role_name()] = self.create_credentials_json(response)
        except Exception:
            self.logger.exception("Could not assume the AWS role:")

        return results

    @staticmethod
    def get_session_name():
        return 'alppaca-on-' + socket.gethostname()

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
