from unittest import TestCase
import datetime

from alppaca.delaytrigger import DelayTrigger
from mock import patch

class FixedDateTime(datetime.datetime):
    """ As unfortunately datetime.datetime.now can not be mocked, since it is an c-extension.
    We use this derived class and override now.

    http://stackoverflow.com/questions/4481954/python-trying-to-mock-datetime-date-today-but-not-working

    """
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(1970, 01, 01, tzinfo=tz)

class DelayTriggerTest(TestCase):

    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_computes_time_delta_for_datetrigger(self, datetrigger_mock):

        datetime.datetime = FixedDateTime

        DelayTrigger(10)

        datetrigger_mock.assert_called_with(run_date=datetime.datetime(1970, 01, 01, 0, 0, 10))

    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_should_call_with_none_if_called_with_negative_delta(self, datetrigger_mock):

        DelayTrigger(-10)

        datetrigger_mock.assert_called_with(run_date=None)