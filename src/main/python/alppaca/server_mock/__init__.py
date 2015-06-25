from bottle import route, run, Bottle

""" Super simple IMS mock.

Just listens on localhost:8080 for the appropriate url, returns a test role and
a dummy json response.

"""

class MockIms(Bottle):

    PATH = '/latest/meta-data/iam/security-credentials/'
    json_response = '{"Code": "Success", ' \
                    '"AccessKeyId": "ASIAI", ' \
                    '"SecretAccessKey": "oieDhF", ' \
                    '"Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", ' \
                    '"Expiration": "2015-04-17T13:40:18Z", ' \
                    '"Type": "AWS-HMAC"}'

    def __init__(self):
        super(MockIms, self).__init__()

        self.route(self.PATH, callback=self.get_roles)
        self.route(self.PATH + '<role>', callback=self.get_credentials)

    def get_roles(self):
        return 'test_role'

    def get_credentials(self, role):
        return self.json_response if role == 'test_role' else ''



if __name__ == "__main__":
    MockIms().run()
