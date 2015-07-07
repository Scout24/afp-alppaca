import mock
from webtest import TestApp

from alppaca.webapp import WebApp
from alppaca.compat import unittest, OrderedDict
from test_utils import json_response


class WebAppTest(unittest.TestCase):

    def setUp(self):
        self.bottle_app = WebApp(mock.Mock())
        self.app = TestApp(self.bottle_app)

    def test_server_is_up_and_running(self):
        self.bottle_app.credentials = {'test_role': json_response}
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, 'test_role')

    def test_server_is_up_and_running_with_multiple_roles(self):
        self.bottle_app.credentials = OrderedDict((('test_role1', json_response),
                                                   ('test_role2', json_response)))
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, 'test_role1\ntest_role2')

    def test_server_delivers_credentials_from_cache(self):
        self.bottle_app.credentials = {'test_role': json_response}
        response = self.app.get('/latest/meta-data/iam/security-credentials/test_role')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, json_response)

    def test_server_delivers_empty_string_on_non_existent_cache(self):
        self.bottle_app.credentials = {}
        response = self.app.get('/latest/meta-data/iam/security-credentials/no_role')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.text, "")





