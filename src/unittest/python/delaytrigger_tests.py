from unittest import TestCase
import datetime

from alppaca.delaytrigger import DelayTrigger
from mock import patch


class DelayTriggerTest(TestCase):

    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_computes_time_delta_for_datetrigger(self, datetrigger_mock):
        class FixedDateTime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return datetime.datetime(2015, 6, 22)

        datetime.datetime = FixedDateTime

        DelayTrigger(10)

        datetrigger_mock.assert_called_with(run_date=datetime.datetime(2015, 06, 22, 0, 0, 10))

    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_compute_time_delta_for_negative_delta(self, datetrigger_mock):
        class FixedDateTime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return datetime.datetime(2015, 6, 22)

        datetime.datetime = FixedDateTime

        DelayTrigger(-10)

        datetrigger_mock.assert_called_with(run_date=None)