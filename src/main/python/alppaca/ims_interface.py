import requests

from util import init_logging
from compat import OrderedDict


class NoRolesFoundException(Exception):
    pass


class NoCredentialsFoundException(Exception):
    pass


class IMSInterface(object):

    def __init__(self, ims_url, debug=False):
        self.ims_host = ims_url
        self.logger = init_logging(debug)

    def get_roles(self):
        try:
            response = requests.get("http://{0}/latest/meta-data/iam/security-credentials/".format(self.ims_host))

            if response.status_code == 200:
                if not response.content:
                    raise NoRolesFoundException("Server response was empty; host has no roles?")

                roles_list = [line.strip() for line in response.content.split("\n")] if response.content else []
                self.logger.debug("Loaded roles: {0}".format(roles_list))
                return roles_list
            else:
                response.raise_for_status()
        except Exception as e:
            self.logger.exception("Due to following cause:")
            raise NoRolesFoundException(e.message)

    def get_credentials(self, role):
        try:
            response = requests.get("http://{0}/latest/meta-data/iam/security-credentials/{1}".format(
                self.ims_host, role))
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
        results = OrderedDict()

        try:
            for role in self.get_roles():
                results[role] = self.get_credentials(role)
        except NoCredentialsFoundException:
            self.logger.exception("Role {0} didn't have any credentials.".format(role))
        return results
