from __future__ import print_function, absolute_import, unicode_literals, division

import requests
import logging

from alppaca.compat import OrderedDict


class NoRolesFoundException(Exception):
    pass


class NoCredentialsFoundException(Exception):
    pass


class IMSCredentialsProvider(object):

    def __init__(self, ims_url, ims_protocol="https", debug=False):
        self.ims_host = ims_url
        self.ims_protocol = ims_protocol
        self.logger = logging.getLogger(__name__)

    def get_roles(self):
        """ Obtain a role. """
        try:
            request_template = "{protocol}://{host}/latest/meta-data/iam/security-credentials/"
            request_url = request_template.format(
                protocol=self.ims_protocol,
                host=self.ims_host)
            self.logger.debug("Requesting Roles from '%s'", request_url)
            response = requests.get(request_url)

            if response.status_code == 200:
                if not response.text:
                    self.logger.debug("Request for roles successful, but empty response")
                    raise NoRolesFoundException("Server response was empty; host has no roles?")

                roles_list = [line.strip() for line in response.text.split("\n")] if response.text else []
                self.logger.debug("Received roles: {0}".format(roles_list))
                return roles_list
            else:
                self.logger.error('Request to "%s" failed', request_url)
                response.raise_for_status()
        except Exception as e:
            self.logger.exception("Error getting roles:")
            raise NoRolesFoundException(str(e))

    def get_credentials(self, role):
        """" Obtain a set of temporary credentials given a role. """
        try:
            request_template = "{protocol}://{host}/latest/meta-data/iam/security-credentials/{role}"
            request_url = request_template.format(
                protocol=self.ims_protocol,
                host=self.ims_host,
                role=role)
            self.logger.debug("Requesting Credentials from '%s'", request_url)
            response = requests.get(request_url)
            if response.status_code == 200:
                if not response.text:
                    self.logger.debug("Request for credentials successful, but empty response")
                    raise NoCredentialsFoundException("Server response was empty; no credentials for role: {0}".format(role))
                self.logger.debug("Request for credentials successful")
                return response.text
            else:
                self.logger.error('Request for credentials to "%s" failed', request_url)
                response.raise_for_status()
        except Exception as e:
            self.logger.exception("Error getting credentials:")
            raise NoCredentialsFoundException(str(e))

    def get_credentials_for_all_roles(self):
        """ Obtain all credentials for all roles. """
        results = OrderedDict()

        try:
            for role in self.get_roles():
                try:
                    results[role] = self.get_credentials(role)
                except NoCredentialsFoundException:
                    self.logger.exception("Role %s didn't have any credentials.", role)
        except NoRolesFoundException:
            self.logger.exception("Could not find any roles")
            raise
        return results
