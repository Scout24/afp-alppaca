import requests

class IMSInterface(object):
    def __init__(self, ims_url):
        self.ims_url = ims_url

    def get_ims_credentials(self):
        pass

    def get_roles(self):
        try:
            response = requests.get("http://{0}/latest/meta-data/iam/security-credentials/".format(self.ims_url))

            roles_list = self._convert_multiline_string_to_list(response.content)
            self.logger.debug("Loaded roles: {0}".format(roles_list))
            assert roles_list, "No roles supplied by upstream server"

            return roles_list
        except Exception as e:
            self.logger.error("Could not fetch roles from {0}: {1}".format(self.ims_url, e))

        raise NoCredentialsException("Could not load roles from any configured metadata server")