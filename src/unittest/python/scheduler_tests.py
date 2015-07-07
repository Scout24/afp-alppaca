import datetime

from mock import Mock, patch
import pytz

from alppaca.scheduler import (Scheduler,
                               backoff_refresh_generator,
                               convert_rfc3339_to_datetime,
                               extract_min_expiration,
                               )
from alppaca.compat import OrderedDict, unittest
from test_utils import FixedDateTime


class TestBackoffRefereshGenerator(unittest.TestCase):

    def test_should_generate_correct_sequence(self):
        expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10]
        brg = backoff_refresh_generator()
        received = [brg.next() for _ in range(15)]
        self.assertEqual(expected, received)


class RefreshCredentialsTest(unittest.TestCase):

    def setUp(self):
        self.credentials_mock = {}
        self.ims_interface_mock = Mock()
        self.scheduler = Scheduler(self.credentials_mock, self.ims_interface_mock)

    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_should_get_valid_credentials_when_called_with_correct_date(self, build_trigger_mock):

        self.ims_interface_mock.get_credentials_for_all_roles.return_value = {
            'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'
        }

        self.scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(0)

    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_should_enter_backoff_state_on_empty_credentials(self, build_trigger_mock):
        self.ims_interface_mock.get_credentials_for_all_roles.return_value = {}

        self.assertIsNone(self.scheduler.backoff)
        self.scheduler.refresh_credentials()
        self.assertIsNotNone(self.scheduler.backoff)

    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_should_increment_refresh_delta_when_in_backoff_state(self, build_trigger_mock):
        self.ims_interface_mock.get_credentials_for_all_roles.return_value = {}
        self.scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(0)
        self.scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(1)
        self.scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(2)

    @patch('datetime.datetime', FixedDateTime)
    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_should_exit_backoff_state_on_valid_credentials(self, build_trigger_mock):
        self.ims_interface_mock.get_credentials_for_all_roles.return_value = {
            'test_role': '{"Expiration": "1970-01-01T00:00:59Z"}'
        }
        self.scheduler.backoff = True
        self.scheduler.refresh_credentials()
        self.assertIsNone(self.scheduler.backoff)

    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_should_enter_backoff_state_on_expired_credentials(self, build_trigger_mock):
        self.ims_interface_mock.get_credentials_for_all_roles.return_value = {
            'test_role': '{"Expiration": "1969-12-24T00:00:00Z"}'
        }
        self.scheduler.refresh_credentials()

        self.assertIsNotNone(self.scheduler.backoff)


class AcquireValidCredentialsTest(unittest.TestCase):
    @patch('alppaca.scheduler.BackgroundScheduler')
    def test_should_acquire_valid_credentials(self, scheduler_mock):
        credentials_mock = OrderedDict()
        ims_interface_mock = Mock()
        expected = OrderedDict({'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'})
        ims_interface_mock.get_credentials_for_all_roles.return_value = expected
        scheduler = Scheduler(credentials_mock, ims_interface_mock)
        scheduler.refresh_credentials()
        self.assertEqual(expected, credentials_mock)

class TestExtractRefreshDelta(unittest.TestCase):

    @patch('datetime.datetime', FixedDateTime)
    def test_should_extract_correct_seconds_from_credentials(self):
        credentials = {'test_role': '{"Expiration": "1970-01-01T00:00:59Z"}'}
        scheduler = Scheduler(credentials, None)
        expected = 59
        received = scheduler.extract_refresh_delta()
        self.assertEqual(expected, received)


class ConvertToDatetimeTest(TestCase):

    def test(self):
        input_ = "1970-01-01T00:00:00Z"
        expected = datetime.datetime(1970, 01, 01, 00, 00, 00, tzinfo=pytz.utc)
        received = convert_rfc3339_to_datetime(input_)
        self.assertEqual(expected, received)


class ExtractMinExpirationTest(TestCase):

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

    def test_should_raise_exception_on_empty_credentials(self):
        input_ = {}
        self.assertRaises(ValueError, extract_min_expiration, input_)
