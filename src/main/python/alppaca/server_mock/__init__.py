from datetime import datetime, timedelta
from textwrap import dedent

from bottle import Bottle
import pytz

""" Super simple IMS mock.

Just listens on localhost:8080 for the appropriate url, returns a test role and
a dummy JSON response.

"""


def expiration_10s_from_now():
    n = datetime.now(tz=pytz.utc) + timedelta(seconds=10)
    return n.strftime("%Y-%m-%dT%H:%M:%SZ")


class MockIms(Bottle):

    PATH = '/latest/meta-data/iam/security-credentials/'
    json_response = dedent("""
                           {"Code": "Success",
                           "AccessKeyId": "ASIAI",
                           "SecretAccessKey": "XXYYZZ",
                           "Token": "0123456789abcdefghijklmnopqrstuvwxyzAB",
                           "Expiration": "%s",
                           "Type": "AWS-HMAC"}
                           """)

    def __init__(self):
        super(MockIms, self).__init__()

        self.route(self.PATH, callback=self.get_roles)
        self.route(self.PATH + '<role>', callback=self.get_credentials)

    def get_roles(self):
        return 'test_role'

    def get_credentials(self, role):
        return self.json_response % expiration_10s_from_now() if role == 'test_role' else ''

if __name__ == "__main__":
    MockIms().run()
