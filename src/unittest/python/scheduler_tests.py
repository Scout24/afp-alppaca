import datetime

from mock import Mock, patch
import pytz
from unittest import TestCase
from alppaca.scheduler import Scheduler
from alppaca.compat import OrderedDict

class FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(2015, 6, 22, tzinfo=tz)


class RefreshCredentialsTest(TestCase):
    @patch('alppaca.scheduler.Scheduler.build_trigger')
    def test_get_credentials_with_correct_date(self, build_trigger_mock):
        credentials_mock = {}
        ims_interface_mock = Mock()
        ims_interface_mock.get_credentials_for_all_roles.return_value = {
            'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'
        }
        
        scheduler = Scheduler(credentials_mock, ims_interface_mock)
        scheduler.refresh_credentials()
        build_trigger_mock.assert_called_with(0)


class AcquireValidCredentialsTest(TestCase):
    @patch('alppaca.scheduler.BackgroundScheduler')
    def test_should_acquire_valid_credentials(self, scheduler_mock):
        credentials_mock = OrderedDict()
        ims_interface_mock = Mock()
        expected = OrderedDict({'test_role': '{"Expiration": "1970-01-01T00:00:00Z"}'})
        ims_interface_mock.get_credentials_for_all_roles.return_value = expected
        scheduler = Scheduler(credentials_mock, ims_interface_mock)
        scheduler.refresh_credentials()
        self.assertEqual(expected, credentials_mock)

class TestDetermineRefreshDelta(TestCase):

    def utility(self, expected, expiration):

        with patch('alppaca.scheduler.uniform') as uniform_mock:
            datetime.datetime = FixedDateTime
            uniform_mock.return_value = 1.2

            scheduler = Scheduler(Mock(), Mock())

            received = scheduler.determine_refresh_delta(expiration)

            self.assertEqual(expected, received)

    def test_should_return_valid_refresh_delta(self):

        expiration = datetime.datetime(2015, 6, 22, 0, 0, 12, tzinfo=pytz.utc)
        expected = 10
        self.utility(expected, expiration)

    def test_build_trigger_calculates_time_delta_with_zero_delta(self):

        expiration = datetime.datetime(2015, 6, 22, tzinfo=pytz.utc)
        expected = 0
        self.utility(expected, expiration)

    def test_should_return_valid_refresh_delta_with_more_than_one_day_delta(self):

        expiration = datetime.datetime(2015, 6, 23, 2, tzinfo=pytz.utc)
        expected = 78000
        self.utility(expected, expiration)

    def test_build_trigger_calculates_time_delta_with_negative_delta(self):

        expiration= datetime.datetime(2015, 6, 21, 2, tzinfo=pytz.utc)
        expected = 0
        self.utility(expected, expiration)