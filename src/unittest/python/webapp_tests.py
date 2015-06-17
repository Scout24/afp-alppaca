from unittest import TestCase

import mock
from webtest import TestApp

from alppaca import bottle_app

json_response = '\'{"Code": "Success", ' \
                '"AccessKeyId": "ASIAI", ' \
                '"SecretAccessKey": "oieDhF", ' \
                '"Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", ' \
                '"Expiration": "2015-04-17T13:40:18Z", ' \
                '"Type": "AWS-HMAC"}\''


class AwsInstanceMetadataClientTest(TestCase):

    def setUp(self):
        self.app = TestApp(bottle_app)

    @mock.patch('alppaca.webapp.roles', ['test_role'])
    def test_server_is_up_and_running(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, 'test_role')

    @mock.patch('alppaca.webapp.roles', ['test_role1', 'test_role2'])
    def test_server_is_up_and_running_with_multiple_roles(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, 'test_role1\ntest_role2')

    @mock.patch.dict('alppaca.webapp.credentials', {'test_role': json_response})
    def test_server_delivers_credentials_from_cache(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/test_role')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, json_response)

    @mock.patch.dict('alppaca.webapp.credentials', {})
    def test_server_delivers_empty_string_on_non_existent_cache(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/no_role')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, "")
