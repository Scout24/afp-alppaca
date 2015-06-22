from unittest import TestCase
import datetime

from alppaca.afterxminstrigger import AfterXMinsTrigger
from mock import patch


class AfterXMinsTriggerTest(TestCase):

    @patch('alppaca.afterxminstrigger.DateTrigger.__init__')
    def test_computes_time_delta_for_datetrigger(self, datetrigger_mock):
        class FixedDateTime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return datetime.datetime(2015, 6, 22)

        datetime.datetime = FixedDateTime

        AfterXMinsTrigger(10)

        datetrigger_mock.assert_called_with(run_date=datetime.datetime(2015, 06, 22, 0, 10))