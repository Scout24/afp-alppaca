from __future__ import print_function, absolute_import, unicode_literals, division

from bottle import Bottle


class WebApp(Bottle):
    """ Main web application that handles HTTP requests. """

    PATH = '/latest/meta-data/iam/security-credentials/'

    def __init__(self, credentials):
        super(WebApp, self).__init__()
        self.credentials = credentials

        self.route(self.PATH, callback=self.get_roles)
        self.route(self.PATH + '<role>', callback=self.get_credentials)

    def get_roles(self):
        """ Return list of roles separated by new-line. """
        return "\n".join(self.credentials.keys())

    def get_credentials(self, role):
        """ Return JSON credentials for a given role. """
        try:
            return self.credentials[role]
        except KeyError:
            return ""
