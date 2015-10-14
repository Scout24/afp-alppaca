from __future__ import print_function, absolute_import, unicode_literals, division

import json

from mock import patch, Mock

from alppaca import NoCredentialsFoundException
from alppaca.compat import OrderedDict, unittest
from alppaca.assume_role import AssumedRoleCredentialsProvider

from boto.sts.credentials import AssumedRole
from boto.sts.credentials import Credentials


ROLE = 'my_role'
ROLE_ARN = 'arn:aws:iam::123456789012:role/%s' % ROLE
ANOTHER_EXPIRATION = "NEW_EXPI"
ANOTHER_TOKEN = "NEW_TOKEN"
ANOTHER_SECRET = "NEW_SECRET"
ANOTHER_KEY = "NEW_KEY"
DUMMY_CREDENTIALS = {'ims_role': '{"AccessKeyId": "ACCESS_KEY", "SecretAccessKey": "SECRET", "Token": "MY_TOKEN"}'}


class AssumeRoleCredentialsProviderTest(unittest.TestCase):


    def setUp(self):
        self.credentials_provider_mock = Mock()
        self.provider = AssumedRoleCredentialsProvider(self.credentials_provider_mock, ROLE_ARN)

    def test_should_raise_exception_for_incomplete_given_credentials(self):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = None
        with self.assertRaises(NoCredentialsFoundException):
            self.provider.get_credentials_for_all_roles()

    @patch('alppaca.assume_role.connect_to_region')
    def test_should_give_credentials(self, sts_mock):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = DUMMY_CREDENTIALS

        given_credentials = Credentials()
        given_credentials.access_key = ANOTHER_KEY
        given_credentials.secret_key = ANOTHER_SECRET
        given_credentials.session_token = ANOTHER_TOKEN
        given_credentials.expiration = ANOTHER_EXPIRATION
        given_credentials_string = json.dumps({
            "AccessKeyId": ANOTHER_KEY,
            "SecretAccessKey": ANOTHER_SECRET,
            "Token": ANOTHER_TOKEN,
            "Expiration": ANOTHER_EXPIRATION
        })

        sts_mock.return_value.assume_role.return_value = AssumedRole(credentials=given_credentials)

        credentials = self.provider.get_credentials_for_all_roles()
        self.assertEqual(given_credentials_string, credentials[ROLE])

    @patch('alppaca.assume_role.connect_to_region')
    def test_should_return_empty_dict_for_failed_boto_call(self, sts_mock):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = DUMMY_CREDENTIALS
        sts_mock.return_value.assume_role.side_effect = Exception('Boom!')
        result = self.provider.get_credentials_for_all_roles()
        self.assertEqual(result, OrderedDict())

if __name__ == '__main__':
    unittest.main()
