from unittest import TestCase
import datetime

from alppaca.delaytrigger import DelayTrigger
from test_utils import FixedDateTime
from mock import patch


class DelayTriggerTest(TestCase):

    @patch('datetime.datetime', FixedDateTime)
    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_should_compute_time_delta_for_datetrigger_for_a_given_date(self, datetrigger_mock):

        DelayTrigger(10)

        datetrigger_mock.assert_called_with(run_date=datetime.datetime(1970, 01, 01, 0, 0, 10))

    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_should_call_datetrigger_with_none_if_called_with_negative_delta(self, datetrigger_mock):

        DelayTrigger(-10)

        datetrigger_mock.assert_called_with(run_date=None)
