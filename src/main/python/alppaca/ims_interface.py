import requests

from util import init_logging
from compat import OrderedDict


class NoRolesFoundException(Exception):
    pass


class NoCredentialsFoundException(Exception):
    pass


class IMSInterface(object):

    def __init__(self, ims_url, ims_protocol="https", debug=False):
        self.ims_host = ims_url
        self.ims_protocol = ims_protocol
        self.logger = init_logging(debug)

    def get_roles(self):
        """ Obtain a role. """
        try:
            request_template = "{protocol}://{host}/latest/meta-data/iam/security-credentials/"
            request_url = request_template.format(
                protocol=self.ims_protocol,
                host=self.ims_host)
            response = requests.get(request_url)

            if response.status_code == 200:
                if not response.content:
                    raise NoRolesFoundException("Server response was empty; host has no roles?")

                roles_list = [line.strip() for line in response.content.split("\n")] if response.content else []
                self.logger.debug("Loaded roles: {0}".format(roles_list))
                return roles_list
            else:
                self.logger.error('Request to "{0}" failed'.format(
                    request_url))
                response.raise_for_status()
        except Exception as e:
            self.logger.exception("Due to following cause:")
            raise NoRolesFoundException(e.message)

    def get_credentials(self, role):
        """" Obtain a set of temporary credentials given a role. """
        try:
            request_template = "{protocol}://{host}/latest/meta-data/iam/security-credentials/{role}"
            response = requests.get(request_template.format(
                protocol=self.ims_protocol,
                host=self.ims_host,
                role=role))
            if response.status_code == 200:
                if not response.content:
                    raise NoCredentialsFoundException("Server response was empty; no credentials for role?")
                return response.content
            else:
                response.raise_for_status()
        except Exception as e:
            self.logger.exception("Due to following cause:")
            raise NoCredentialsFoundException(e.message)

    def get_credentials_for_all_roles(self):
        """ Obtain all credentials for all roles. """
        results = OrderedDict()

        try:
            for role in self.get_roles():
                try:
                    results[role] = self.get_credentials(role)
                except NoCredentialsFoundException:
                    self.logger.exception("Role {0} didn't have any credentials.".format(role))
        except NoRolesFoundException:
            self.logger.exception("Could not find any roles")
        return results
