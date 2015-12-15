from __future__ import print_function, absolute_import, unicode_literals, division

import textwrap

import mock
import requests_mock
import requests
import logging

from afp_alppaca import IMSCredentialsProvider, NoRolesFoundException, NoCredentialsFoundException
from afp_alppaca.compat import unittest
from test_utils import json_response


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(module)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.DEBUG)


class IMSCredentialsProviderTestGetRoles(unittest.TestCase):

    def setUp(self):
        self.imsi = IMSCredentialsProvider("no-such-host.invalid", ims_protocol="http")

    @requests_mock.mock()
    def test_should_get_valid_role_when_single_role_is_given(self, mock_object):
        mock_object.get(requests_mock.ANY, text="test_role")
        received_roles = self.imsi.get_roles()
        expected_roles = ["test_role"]
        self.assertEqual(expected_roles, received_roles)

    @requests_mock.mock()
    def test_should_get_valid_roles_when_multiple_roles_are_given(self, mock_object):
        mock_object.get(requests_mock.ANY, text="test_role1\ntest_role2\n test_role3")
        received_roles = self.imsi.get_roles()
        expected_roles = ["test_role1", "test_role2", "test_role3"]
        self.assertEqual(expected_roles, received_roles)

    @requests_mock.mock()
    def test_should_raise_no_roles_found_exception_when_empty_response_is_received(self, mock_object):
        mock_object.get(requests_mock.ANY, text="")
        self.assertRaises(NoRolesFoundException, self.imsi.get_roles)

    @mock.patch("requests.get")
    def test_should_raise_no_roles_found_exception_when_bad_host_is_given(self, mock_object):
        mock_object.side_effect = [requests.ConnectionError("Could not resolve host")]
        self.assertRaises(NoRolesFoundException, self.imsi.get_roles)

    @requests_mock.mock()
    def test_should_get_role_url(self, mock_object):
        mock_object.get("http://no-such-host.invalid/latest/meta-data/iam/security-credentials/", text="test_role")
        self.imsi.get_roles()

    @requests_mock.mock()
    def test_should_raise_no_roles_found_exception_when_http_status_error_is_received(self, mock_object):
        mock_object.get(requests_mock.ANY, status_code=400)
        self.assertRaises(NoRolesFoundException, self.imsi.get_roles)


class IMSCredentialsProviderTestGetCredentials(unittest.TestCase):
    def setUp(self):
        self.imsi = IMSCredentialsProvider("no-such-host.invalid", ims_protocol="http")
        self.json_response = json_response

    @requests_mock.mock()
    def test_should_get_valid_credentials_when_called_with_single_role(self, mock_object):
        mock_object.get(requests_mock.ANY, text=self.json_response)
        received_credentials = self.imsi.get_credentials("test_role")
        self.assertEqual(self.json_response, received_credentials)

    @requests_mock.mock()
    def test_should_raise_no_credentials_found_exception_when_empty_response_is_received(self, mock_object):
        mock_object.get(requests_mock.ANY, text="")
        self.assertRaises(NoCredentialsFoundException, self.imsi.get_credentials, "test_role")

    @requests_mock.mock()
    def test_should_raise_no_credentials_found_exception_when_http_status_error_is_received(self, mock_object):
        mock_object.get(requests_mock.ANY, status_code=400)
        self.assertRaises(NoCredentialsFoundException, self.imsi.get_credentials, "test_role")

    @requests_mock.mock()
    def test_should_raise_no_credentials_found_exception_when_role_can_not_be_assumed(self, mock_object):
        response = textwrap.dedent("""
                                   {"timestamp":1436349287404,
                                    "status":500,
                                    "error":"Internal Server Error",
                                    "exception":"com.amazonaws.AmazonServiceException",
                                    "message":"User: arn:aws:iam::XXXXXXXXXXXX:user/federation-user-proxy
                                     is not authorized to perform: sts:AssumeRole
                                     on resource: arn:aws:iam::XXXXXXXXXXXX:role/rz_devesc
                                     (Service: AWSSecurityTokenService; Status Code: 403;
                                      Error Code: AccessDenied; Request ID:
                                      5df35a2d-2557-11e5-8899-b7abe26301a6)",
                                    "path":"/latest/meta-data/iam/security-credentials/rz_devesc"}
                                   """)
        mock_object.get(requests_mock.ANY, status_code=500, text=response)
        self.assertRaises(NoCredentialsFoundException, self.imsi.get_credentials, "test_role")

class IMSCredentialsProviderTestGetCredentialsForAllRoles(unittest.TestCase):
    def setUp(self):
        self.imsi = IMSCredentialsProvider("no-such-host.invalid", ims_protocol="http")
        self.json_response = json_response

    @requests_mock.mock()
    def test_should_get_valid_roles_and_credentials_when_called_with_single_role(self, mock_object):
        mock_object.get(requests_mock.ANY, [{'text': 'test_role'}, {'text': self.json_response}])
        received_credentials = self.imsi.get_credentials_for_all_roles()
        self.assertEqual({'test_role': self.json_response}, received_credentials)

    @requests_mock.mock()
    def test_get_roles_and_credentials_when_called_with_multiple_roles(self, mock_object):
        mock_object.get(requests_mock.ANY, [{'text': 'test_role1\ntest_role2'},
                                            {'text': self.json_response},
                                            {'text': self.json_response}
                                            ])
        received_credentials = self.imsi.get_credentials_for_all_roles()
        expected = {'test_role1': self.json_response,
                    'test_role2': self.json_response,
                    }
        self.assertEqual(expected, received_credentials)

    @requests_mock.mock()
    def test_should_get_roles_and_valid_credentials_when_called_with_empty_role(self, mock_object):
        mock_object.get(requests_mock.ANY, [{'text': ''}])
        self.assertRaises(NoRolesFoundException, self.imsi.get_credentials_for_all_roles)

    @requests_mock.mock()
    def test_should_get_roles_and_valid_credentials_when_called_with_empty_credentials(self, mock_object):
        mock_object.get(requests_mock.ANY, [{'text': 'test_role1\n test_role2'},
                                            {'text': self.json_response},
                                            {'text': ''}])
        received_credentials = self.imsi.get_credentials_for_all_roles()
        self.assertEqual({'test_role1': self.json_response}, received_credentials)
