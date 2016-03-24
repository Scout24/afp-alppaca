from __future__ import print_function, absolute_import, unicode_literals, division

import requests
import logging

from afp_alppaca.compat import OrderedDict


class NoRolesFoundException(Exception):
    pass


class NoCredentialsFoundException(Exception):
    pass


class IMSCredentialsProvider(object):
    def __init__(self, ims_host, ims_protocol="https"):
        self.logger = logging.getLogger(__name__)

        get_role_template = (
            "{protocol}://{host}/latest/meta-data/iam/security-credentials/")
        self.get_role_url = get_role_template.format(
                protocol=ims_protocol, host=ims_host)
        self.get_creds_template = self.get_role_url + '{role}'

    def get_roles(self):
        """ Obtain a role. """
        try:
            self.logger.debug("Requesting Roles from '%s'", self.get_role_url)
            response = requests.get(self.get_role_url)

            if response.status_code != 200:
                self.logger.error('Request to "%s" failed', self.get_role_url)
                response.raise_for_status()
            if not response.text:
                self.logger.debug("Request for roles successful, but empty response")
                raise NoRolesFoundException("Server response was empty; host has no roles?")

            roles_list = [line.strip() for line in response.text.split("\n")]
            self.logger.debug("Received roles: {0}".format(roles_list))
            return roles_list
        except Exception as error:
            self.logger.exception("Error getting roles:")
            raise NoRolesFoundException(str(error))

    def get_credentials(self, role):
        """" Obtain a set of temporary credentials given a role. """
        try:
            request_url = self.get_creds_template.format(role=role)
            self.logger.debug("Requesting Credentials from '%s'", request_url)
            response = requests.get(request_url)

            if response.status_code != 200:
                self.logger.error('Request for credentials to "%s" failed', request_url)
                response.raise_for_status()
            if not response.text:
                self.logger.debug("Request for credentials successful, but empty response")
                raise NoCredentialsFoundException(
                    "Server response was empty; no credentials for role: {0}".format(role))

            self.logger.debug("Request for credentials successful")
            return response.text
        except Exception as e:
            self.logger.exception("Error getting credentials for role '%s':", role)
            raise NoCredentialsFoundException(str(e))

    def get_credentials_for_all_roles(self):
        """ Obtain all credentials for all roles. """
        results = OrderedDict()

        try:
            roles = self.get_roles()
        except NoRolesFoundException as error:
            self.logger.warn("Could not find any roles")
            self.logger.debug(str(error))
            raise

        for role in roles:
            try:
                results[role] = self.get_credentials(role)
            except NoCredentialsFoundException:
                self.logger.exception("Role %s didn't have any credentials.", role)
        return results
