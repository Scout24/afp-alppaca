from __future__ import print_function, absolute_import, unicode_literals, division

import datetime
import isodate
import logging

from mock import Mock, patch
import pytz
import six

from afp_alppaca.scheduler import (Scheduler,
                                   backoff_refresh_generator,
                                   extract_min_expiration,
                                   )
from afp_alppaca.compat import OrderedDict, unittest
from afp_alppaca.ims_interface import NoRolesFoundException
from test_utils import FixedDateTime

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(module)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.DEBUG)


class TestBackoffRefereshGenerator(unittest.TestCase):

    def test_should_generate_correct_sequence(self):
        expected = [1.5, 2.25, 3.375, 5.0625, 7.59375, 10, 10, 10, 10, 10]
        brg = backoff_refresh_generator(1.5, 10)
        received = [six.next(brg) for _ in range(10)]
        self.assertEqual(expected, received)


class RefreshCredentialsTest(unittest.TestCase):
    def setUp(self):
        self.credentials_mock = {}
        self.credentials_provider_mock = Mock()
        self.scheduler = Scheduler(self.credentials_mock, self.credentials_provider_mock)

    def test_should_get_valid_credentials_when_called_with_correct_date(self):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = {
            'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'
        }

        next_sleep = self.scheduler._refresh_credentials()
        self.assertEqual(next_sleep, 1.5)

    def test_should_enter_backoff_state_on_empty_credentials(self):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = {}

        self.assertIsNone(self.scheduler.backoff)
        self.scheduler._refresh_credentials()
        self.assertIsNotNone(self.scheduler.backoff)

    def test_should_increment_refresh_delta_when_in_backoff_state(self):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = {}
        next_sleep = self.scheduler._refresh_credentials()
        self.assertEqual(next_sleep, 1.5)
        next_sleep = self.scheduler._refresh_credentials()
        self.assertEqual(next_sleep, 2.25)
        next_sleep = self.scheduler._refresh_credentials()
        self.assertEqual(next_sleep, 3.375)

    @patch('datetime.datetime', FixedDateTime)
    def test_should_exit_backoff_state_on_valid_credentials(self):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = {
                'test_role': '{"Expiration": "1970-01-01T00:00:59Z"}'
        }
        self.scheduler.backoff = True
        self.scheduler._refresh_credentials()
        self.assertIsNone(self.scheduler.backoff)

    def test_should_enter_backoff_state_on_expired_credentials(self):
        self.credentials_provider_mock.get_credentials_for_all_roles.return_value = {
                'test_role': '{"Expiration": "1969-12-24T00:00:00Z"}'
        }
        self.scheduler._refresh_credentials()

        self.assertIsNotNone(self.scheduler.backoff)

    def test_should_enter_backoff_state_on_exception(self):
        self.credentials_provider_mock.get_credentials_for_all_roles.side_effect = Exception()
        self.scheduler._refresh_credentials()

        self.assertIsNotNone(self.scheduler.backoff)

    @patch('afp_alppaca.scheduler.Scheduler.do_backoff')
    def test_should_enter_backoff_state_on_no_roles_found_exception(self, do_backoff_mock):
        self.credentials_provider_mock.get_credentials_for_all_roles.side_effect = NoRolesFoundException()
        self.scheduler._refresh_credentials()
        do_backoff_mock.assert_called_with(factor=3, max_interval=300)

    @patch('afp_alppaca.scheduler.time.sleep')
    def test_eternal_loop_sleeps_correctly(self, mock_sleep):
        # The eternal loop does not catch BaseExceptions. This is used
        # to make it a bit less eternal.
        class TestException(BaseException):
            pass
        mock_refresh = Mock()
        mock_refresh.side_effect = [4242, TestException]
        self.scheduler._refresh_credentials = mock_refresh

        with self.assertLogs(level=logging.DEBUG) as cm:
            self.assertRaises(TestException, self.scheduler.refresh_credentials)

        mock_refresh.assert_called_with()
        mock_sleep.assert_called_with(4242)

        # refresh_credentials must log how long it will sleep.
        all_log_messages = "".join(cm.output)
        self.assertIn("4242", all_log_messages)

    @patch('afp_alppaca.scheduler.time.sleep')
    def test_eternal_loop_catches_exceptions(self, mock_sleep):
        # The eternal loop does not catch BaseExceptions. This is used
        # to make it a bit less eternal.
        class TestException(BaseException):
            pass

        mock_refresh = Mock()
        mock_refresh.side_effect = [Exception("123 unit testing"), TestException]
        self.scheduler._refresh_credentials = mock_refresh

        with self.assertLogs(level=logging.ERROR) as cm:
            self.assertRaises(TestException, self.scheduler.refresh_credentials)

        mock_refresh.assert_called_with()
        # Default sleep time in case of uncaught exceptions is 120 seconds.
        mock_sleep.assert_called_with(120)

        # Exception message must have been logged.
        all_log_messages = "".join(cm.output)
        self.assertIn("123 unit testing", all_log_messages)

class AcquireValidCredentialsTest(unittest.TestCase):
    def test_should_acquire_valid_credentials(self):
        credentials_mock = OrderedDict()
        credentials_provider_mock = Mock()
        expected = OrderedDict({'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'})
        credentials_provider_mock.get_credentials_for_all_roles.return_value = expected
        scheduler = Scheduler(credentials_mock, credentials_provider_mock)
        scheduler._refresh_credentials()
        self.assertEqual(expected, credentials_mock)

    def test_should_keep_valid_credentials_if_refresh_fails(self):
        credentials_mock = OrderedDict()
        credentials_provider_mock = Mock()
        expected = OrderedDict({'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'})
        credentials_provider_mock.get_credentials_for_all_roles.return_value = expected
        scheduler = Scheduler(credentials_mock, credentials_provider_mock)
        scheduler._refresh_credentials()
        self.assertEqual(expected, credentials_mock)

        # now, let's send in no credentials
        credentials_provider_mock.get_credentials_for_all_roles.return_value = {}
        scheduler._refresh_credentials()
        self.assertEqual(expected, credentials_mock)
        self.assertIsNotNone(scheduler.backoff)


class TestExtractRefreshDelta(unittest.TestCase):

    @patch('datetime.datetime', FixedDateTime)
    def test_should_extract_correct_seconds_from_credentials(self):
        credentials = {'test_role': '{"Expiration": "1970-01-01T00:00:59Z"}'}
        scheduler = Scheduler(credentials, None)
        expected = 59
        received = scheduler.extract_refresh_delta()
        self.assertEqual(expected, received)

    @patch('datetime.datetime', FixedDateTime)
    def test_should_allow_milliseconds_in_expiration(self):
        """Moto has milliseconds in the expiration date, AWS does not"""
        credentials = {'test_role': '{"Expiration": "1970-01-01T00:00:59.123Z"}'}
        scheduler = Scheduler(credentials, None)
        expected = 59
        received = scheduler.extract_refresh_delta()
        self.assertEqual(expected, received)


class ConvertToDatetimeTest(unittest.TestCase):

    def test(self):
        input_ = "1970-01-01T00:00:00Z"
        expected = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        received = isodate.parse_datetime(input_)
        self.assertEqual(expected, received)


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

    def test_should_raise_exception_on_empty_credentials(self):
        input_ = {}
        self.assertRaises(ValueError, extract_min_expiration, input_)
