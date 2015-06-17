try:
    import unittest2 as unittest
except ImportError:
    import unittest

import mock
import requests_mock
import requests

from alppaca import IMSInterface, NoRolesFoundException, NoCredentialsFoundException



class IMSInterfaceTestGetRoles(unittest.TestCase):

    def setUp(self):
        self.imsi = IMSInterface("no-such-host.com")
    
    @requests_mock.mock()
    def test_get_role_for_single_role(self, mock_object):
        mock_object.get(requests_mock.ANY, text="test_role")
        received_roles = self.imsi.get_roles()
        expected_roles = ["test_role"]
        self.assertEqual(expected_roles, received_roles)

    @requests_mock.mock()
    def test_get_role_for_multiple_roles(self, mock_object):
        mock_object.get(requests_mock.ANY, text="test_role1\ntest_role2\n test_role3")
        received_roles = self.imsi.get_roles()
        expected_roles = ["test_role1", "test_role2", "test_role3"]
        self.assertEqual(expected_roles, received_roles)

    @requests_mock.mock()
    def test_get_role_exception_for_empty_response(self, mock_object):
        mock_object.get(requests_mock.ANY, text="")
        self.assertRaises(NoRolesFoundException, self.imsi.get_roles)

    @mock.patch("requests.get")
    def test_get_role_exception_for_bad_host(self, mock_object):
        mock_object.side_effect = [requests.ConnectionError("Could not resolve host")]
        self.assertRaises(NoRolesFoundException, self.imsi.get_roles)

    @requests_mock.mock()
    def test_get_role_url(self, mock_object):
        mock_object.get("http://no-such-host.com/latest/meta-data/iam/security-credentials/", text="test_role")
        self.imsi.get_roles()

    @requests_mock.mock()
    def test_get_role_exception_for_http_status_error(self, mock_object):
        mock_object.get(requests_mock.ANY, status_code=400)
        self.assertRaises(NoRolesFoundException, self.imsi.get_roles)


class IMSInterfaceTestGetCredentials(unittest.TestCase):
    def setUp(self):
        self.imsi = IMSInterface("no-such-host.com")
        self.json_response ='\'{"Code": "Success", "AccessKeyId": "ASIAI", "SecretAccessKey": "oieDhF", ' \
                            '"Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", ' \
                            '"Expiration": "2015-04-17T13:40:18Z", "Type": "AWS-HMAC"}\''
        
    @requests_mock.mock()
    def test_get_credentials_for_single_role(self, mock_object):
        mock_object.get(requests_mock.ANY, text=self.json_response)
        received_credentials = self.imsi.get_credentials("test_role")
        self.assertEqual(self.json_response, received_credentials)

    @requests_mock.mock()
    def test_get_credentials_exception_for_empty_response(self, mock_object):
        mock_object.get(requests_mock.ANY, text="")
        self.assertRaises(NoCredentialsFoundException, self.imsi.get_credentials, "test_role")

    @requests_mock.mock()
    def test_get_credentials_exception_for_http_status_error(self, mock_object):
        mock_object.get(requests_mock.ANY, status_code=400)
        self.assertRaises(NoCredentialsFoundException, self.imsi.get_credentials, "test_role")