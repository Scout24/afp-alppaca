import datetime

from mock import Mock, patch
import pytz
from unittest import TestCase
from alppaca.scheduler import Scheduler


class FixedDateTime(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return datetime.datetime(2015, 6, 22)


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
        build_trigger_mock.assert_called_with(datetime.datetime(1970, 1, 1, tzinfo=pytz.utc))
        
    @patch('alppaca.scheduler.BackgroundScheduler')
    @patch('alppaca.scheduler.DelayTrigger')
    @patch('alppaca.scheduler.uniform')
    def test_build_trigger_calculates_time_delta(self, uniform_mock, trigger_mock, scheduler_mock):

        datetime.datetime = FixedDateTime
        uniform_mock.return_value = 1.2
        
        scheduler = Scheduler(Mock(), Mock())
        scheduler.build_trigger(datetime.datetime(2015, 6, 22, 0, 0, 12))
        
        trigger_mock.assert_called_with(10)

    @patch('alppaca.scheduler.BackgroundScheduler')
    @patch('alppaca.scheduler.DelayTrigger')
    @patch('alppaca.scheduler.uniform')
    def test_build_trigger_calculates_time_delta_with_zero_delta(self, uniform_mock, trigger_mock, scheduler_mock):

        datetime.datetime = FixedDateTime
        uniform_mock.return_value = 1.2

        scheduler = Scheduler(Mock(), Mock())
        scheduler.build_trigger(datetime.datetime(2015, 6, 22))

        trigger_mock.assert_called_with(0)

    @patch('alppaca.scheduler.BackgroundScheduler')
    @patch('alppaca.scheduler.DelayTrigger')
    @patch('alppaca.scheduler.uniform')
    def test_build_trigger_calculates_time_delta_with_more_than_one_day_delta(self, uniform_mock, trigger_mock, scheduler_mock):

        datetime.datetime = FixedDateTime
        uniform_mock.return_value = 1.2

        scheduler = Scheduler(Mock(), Mock())
        scheduler.build_trigger(datetime.datetime(2015, 6, 23, 2))

        trigger_mock.assert_called_with(78000)

    @patch('alppaca.scheduler.BackgroundScheduler')
    @patch('alppaca.scheduler.DelayTrigger')
    @patch('alppaca.scheduler.uniform')
    def test_build_trigger_calculates_time_delta_with_negative_delta(self, uniform_mock, trigger_mock, scheduler_mock):

        datetime.datetime = FixedDateTime
        uniform_mock.return_value = 1.2

        scheduler = Scheduler(Mock(), Mock())
        scheduler.build_trigger(datetime.datetime(2015, 6, 21, 2))

        trigger_mock.assert_called_with(0)