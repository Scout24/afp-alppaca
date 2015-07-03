import datetime

from mock import Mock, patch
import pytz
from alppaca.scheduler import Scheduler, backoff_refresh_generator
from alppaca.compat import OrderedDict
from alppaca.compat import unittest


class FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(2015, 6, 22, tzinfo=tz)


class TestBackoffRefereshGenerator(unittest.TestCase):

    def test_should_generate_correct_sequence(self):
        expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10]
        brg = backoff_refresh_generator()
        received = [brg.next() for _ in range(15)]
        self.assertEqual(expected, received)


class RefreshCredentialsTest(unittest.TestCase):
    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_should_get_valid_credentials_when_called_with_correct_date(self, build_trigger_mock):
        credentials_mock = {}
        ims_interface_mock = Mock()
        ims_interface_mock.get_credentials_for_all_roles.return_value = {
            'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'
        }

        scheduler = Scheduler(credentials_mock, ims_interface_mock)
        scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(0)

    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_should_enter_backoff_state_on_empty_credentials(self, build_trigger_mock):
        credentials_mock = {}
        ims_interface_mock = Mock()
        ims_interface_mock.get_credentials_for_all_roles.return_value = {}

        scheduler = Scheduler(credentials_mock, ims_interface_mock)
        self.assertIsNone(scheduler.backoff)
        scheduler.refresh_credentials()
        self.assertIsNotNone(scheduler.backoff)
        build_trigger_mock.assert_called_with(0)
        scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(1)
        scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(2)
        ims_interface_mock.get_credentials_for_all_roles.return_value = {
            'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'
        }
        scheduler.refresh_credentials()
        self.assertIsNone(scheduler.backoff)
        build_trigger_mock.assert_called_with(0)


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

class TestDetermineRefreshDelta(unittest.TestCase):

    def helper(self, expected, expiration):

        with patch('alppaca.scheduler.uniform') as uniform_mock:
            datetime.datetime = FixedDateTime
            uniform_mock.return_value = expected

            scheduler = Scheduler(Mock(), Mock())

            received = scheduler.determine_refresh_delta(expiration)

            self.assertEqual(expected, received)

    def test_should_return_positive_refresh_delta_when_expiration_is_in_the_future(self):

        expiration = datetime.datetime(2015, 6, 22, 0, 0, 12, tzinfo=pytz.utc)
        expected = 12
        self.helper(expected, expiration)

    def test_should_return_zero_refresh_delta_when_expiration_is_now(self):

        expiration = datetime.datetime(2015, 6, 22, tzinfo=pytz.utc)
        expected = 0
        self.helper(expected, expiration)

    def test_should_return_refresh_delta_with_more_than_one_day_delta_when_called_one_day_in_the_future(self):

        expiration = datetime.datetime(2015, 6, 23, 2, tzinfo=pytz.utc)
        expected = 78000
        self.helper(expected, expiration)

    def test_should_return_zero_time_delta_when_expiration_is_in_the_past(self):

        expiration= datetime.datetime(2015, 6, 21, 2, tzinfo=pytz.utc)
        expected = 0
        self.helper(expected, expiration)

