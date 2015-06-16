try:
    import unittest2 as unittest
except ImportError:
    import unittest

import requests_mock

from alppaca import IMSInterface


class IMSInterfaceTest(unittest.TestCase):
    
    @requests_mock.mock()
    def test_get_ims_credentials_for_single_role(self, mock_object):
        mock_object.get(requests_mock.ANY, text="test_role")
        imsi = IMSInterface("http://no-such-host.com")
        received_roles = imsi.get_roles()
        expected_roles = ["test_role"]
        self.assertEqual(expected_roles, received_roles)