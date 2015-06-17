from unittest import TestCase

import mock
from webtest import TestApp

from alppaca import bottle_app


class AwsInstanceMetadataClientTest(TestCase):

    def setUp(self):
        self.app = TestApp(bottle_app)

    @mock.patch.dict('alppaca.webapp.credentials', {'test_role': ''})
    def test_server_is_up_and_running(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, 'test_role')

    @mock.patch.dict('alppaca.webapp.credentials', {'test_role1': '', 'test_role2': ''})
    def test_server_is_up_and_running_with_multiple_roles(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, 'test_role1\ntest_role2')
