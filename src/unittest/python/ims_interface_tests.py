try:
    import unittest2 as unittest
except ImportError:
    import unittest

import mock
import requests_mock
import requests

from alppaca import IMSInterface, NoRolesFoundException


class IMSInterfaceTest(unittest.TestCase):
    
    @requests_mock.mock()
    def test_get_ims_credentials_for_single_role(self, mock_object):
        mock_object.get(requests_mock.ANY, text="test_role")
        imsi = IMSInterface("http://no-such-host.com")
        received_roles = imsi.get_roles()
        expected_roles = ["test_role"]
        self.assertEqual(expected_roles, received_roles)

    @requests_mock.mock()
    def test_get_ims_credentials_for_multiple_roles(self, mock_object):
        mock_object.get(requests_mock.ANY, text="test_role1\ntest_role2\n test_role3")
        imsi = IMSInterface("http://no-such-host.com")
        received_roles = imsi.get_roles()
        expected_roles = ["test_role1", "test_role2", "test_role3"]
        self.assertEqual(expected_roles, received_roles)

    @requests_mock.mock()
    def test_exception_for_empty_request(self, mock_object):
        mock_object.get(requests_mock.ANY, text="")
        imsi = IMSInterface("http://no-such-host.com")
        self.assertRaises(NoRolesFoundException, imsi.get_roles)

    @mock.patch("requests.get")
    def test_exception_for_bad_host(self, mock_object):
        mock_object.side_effect = [requests.ConnectionError("Could not resolve host")]
        imsi = IMSInterface("http://no-such-host.com")
        self.assertRaises(NoRolesFoundException, imsi.get_roles)

    @requests_mock.mock()
    def test_get_ims_credentials_for_single_role(self, mock_object):
        mock_object.get(requests_mock.ANY, status_code=400)
        imsi = IMSInterface("http://no-such-host.com")
        self.assertEqual(NoRolesFoundException, imsi.get_roles)