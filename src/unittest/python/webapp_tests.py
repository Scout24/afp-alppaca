import json
import unittest
from unittest import TestCase
from alppaca import flask_app
import alppaca
import mock


class AwsInstanceMetadataClientTest(TestCase):

    def setUp(self):
        self.app = flask_app.test_client()

    @mock.patch.dict('alppaca.webapp.credentials', {'test_role': ''})
    def test_server_is_up_and_running(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, 'test_role')

    @mock.patch.dict('alppaca.webapp.credentials', {'test_role1': '', 'test_role2': ''})
    def test_server_is_up_and_running(self):
        response = self.app.get('/latest/meta-data/iam/security-credentials/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, 'test_role1\ntest_role2')
