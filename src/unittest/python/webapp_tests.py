import mock
import datetime
import pytz
from webtest import TestApp

from alppaca.webapp import WebApp, extract_min_expiration, convert_rfc3339_to_datetime
from alppaca.compat import unittest, OrderedDict

json_response = '\'{"Code": "Success", ' \
                '"AccessKeyId": "ASIAI", ' \
                '"SecretAccessKey": "oieDhF", ' \
                '"Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej", ' \
                '"Expiration": "2015-04-17T13:40:18Z", ' \
                '"Type": "AWS-HMAC"}\''


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


class ExtractMinExpirationTest(unittest.TestCase):

    def test_extract_min_expiration_for_single_credential(self):
        input_ = {'test_role':  '{"Expiration": "1970-01-01T00:00:00Z"}'}
        expected = "1970-01-01T00:00:00Z"
        received = extract_min_expiration(input_)
        self.assertEqual(expected, received)

    def test_extract_min_expiration_for_multiple_credentials(self):
        input_ = {'test_role1':  '{"Expiration": "1970-01-01T00:00:00Z"}',
                  'test_role2':  '{"Expiration": "1970-01-01T00:00:01Z"}'}
        expected = "1970-01-01T00:00:00Z"
        received = extract_min_expiration(input_)
        self.assertEqual(expected, received)

    def test_extract_min_expiration_for_multiple_identical_credentials(self):
        input_ = {'test_role1':  '{"Expiration": "1970-01-01T00:00:00Z"}',
                  'test_role2':  '{"Expiration": "1970-01-01T00:00:00Z"}'}
        expected = "1970-01-01T00:00:00Z"
        received = extract_min_expiration(input_)
        self.assertEqual(expected, received)


class ConvertToDatetimeTest(unittest.TestCase):

    def test(self):
        input_ = "1970-01-01T00:00:00Z"
        expected = datetime.datetime(1970, 01, 01, 00, 00, 00, tzinfo=pytz.utc)
        received = convert_rfc3339_to_datetime(input_)
        self.assertEqual(expected, received)


class RefreshCredentialsTest(unittest.TestCase):
    
    @mock.patch('alppaca.webapp.DateTrigger')
    def test_get_credentials_with_correct_date(self, date_trigger_mock):
        credentials_provider = mock.Mock()
        credentials_provider.get_credentials_for_all_roles.return_value \
            = {'test_role':  '{"Expiration": "1970-01-01T00:00:00Z"}'}
        task_scheduler = mock.Mock()
        
        web_app = WebApp(credentials_provider, task_scheduler)
        web_app.refresh_credentials()
        
        task_scheduler.add_job.assert_called_with(func=web_app.refresh_credentials, trigger=mock.ANY)
        date_trigger_mock.assert_called_with(datetime.datetime(1970, 01, 01, 00, 00, 00, tzinfo=pytz.utc))