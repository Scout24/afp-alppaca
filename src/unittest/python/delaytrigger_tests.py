from __future__ import print_function, absolute_import, unicode_literals, division

import datetime
import logging
import os
import six
import time

from mock import patch
import pytz

from alppaca.delaytrigger import DelayTrigger
from alppaca.compat import unittest
from alppaca.scheduler import Scheduler, backoff_refresh_generator
from test_utils import FixedDateTime


class DelayTriggerTest(unittest.TestCase):
    def scheduler_backoff_duration(self, steps, factor, max_interval):
        """Return how long the backoff algorithm needs for given steps

        This ensures the tests keep working even if the backoff algorithm is
        changed.
        """
        seconds = 0
        # The scheduler makes the first step immediately.
        steps -= 1

        generator = backoff_refresh_generator(factor, max_interval)
        for x in range(steps):
            seconds += six.next(generator)

        # Extra time to avoid race conditions.
        seconds += 0.5

        return seconds

    @patch('datetime.datetime', FixedDateTime)
    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_should_compute_time_delta_for_datetrigger_for_a_given_date(self, datetrigger_mock):
        DelayTrigger(10)

        expected_run_date = datetime.datetime(1970, 1, 1, 0, 0, 10, tzinfo=pytz.utc,)
        datetrigger_mock.assert_called_with(run_date=expected_run_date)

    @patch('datetime.datetime', FixedDateTime)
    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_zero_is_a_valid_delay(self, datetrigger_mock):
        DelayTrigger(0)

        expected_run_date = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc,)
        datetrigger_mock.assert_called_with(run_date=expected_run_date)

    @patch('alppaca.delaytrigger.DateTrigger.__init__')
    def test_should_call_datetrigger_with_none_if_called_with_negative_delta(self, datetrigger_mock):
        DelayTrigger(-10)

        datetrigger_mock.assert_called_with(run_date=None)

    @unittest.skip("Will mess up the system time")
    def test_scheduler_in_error_state_handles_winter_to_summer_time(self):
        self.dst_error_state_helper("2016-03-27 01:59:58")

    @unittest.skip("Will mess up the system time")
    def test_scheduler_in_error_state_handles_summer_to_winter_time(self):
        self.dst_error_state_helper("2016-10-30 02:59:58")

    @unittest.skip("Will mess up the system time")
    def test_scheduler_in_good_state_handles_winter_to_summer_time(self):
        self.dst_good_state_helper("2016-03-27 01:59:58")

    @unittest.skip("Will mess up the system time")
    def test_scheduler_in_good_state_handles_summer_to_winter_time(self):
        self.dst_good_state_helper("2016-10-30 02:59:58")

    def dst_error_state_helper(self, date_string_to_test):
        """Helper function to test daylight savings time in ERROR state

        This function uses 'sudo date ....' to modify your system's date. You
        will need to fix this manually.
        """
        logging.warn("\n" * 3 + self.dst_error_state_helper.__doc__)

        os.system('sudo date -s "{0}"'.format(date_string_to_test))

        fake_provider = FakeProvider()
        scheduler = Scheduler({}, fake_provider)

        expected_call_count = 3
        sleep_time = self.scheduler_backoff_duration(expected_call_count, 1.5, 10)

        scheduler.refresh_credentials()
        time.sleep(sleep_time)
        scheduler.scheduler.shutdown()

        self.assertEqual(fake_provider.call_count, expected_call_count)

    def dst_good_state_helper(self, date_string_to_test):
        """Helper function to test daylight savings time in GOOD state

        This function uses 'sudo date ....' to modify your system's date. You
        will need to fix this manually.
        """
        logging.warn("\n" * 3 + self.dst_good_state_helper.__doc__)

        os.system('sudo date -s "{0}"'.format(date_string_to_test))

        fake_provider = FakeProvider(has_credentials=True)
        scheduler = Scheduler({}, fake_provider)

        # Remove randomization of refresh delta.
        scheduler.sample_new_refresh_delta = lambda refresh_delta: refresh_delta / 2.0

        scheduler.refresh_credentials()

        time.sleep(6.5)
        scheduler.scheduler.shutdown()

        # Credentials are valid for 6 seconds. Refreshing looks like this:
        # first fetch...3 seconds...second fetch...3 seconds...third fetch
        self.assertEqual(fake_provider.call_count, 3)


class FakeProvider(object):
    def __init__(self, has_credentials=False):
        self.call_count = 0
        self.has_credentials = has_credentials

    def get_credentials_for_all_roles(self):
        self.call_count += 1
        if not self.has_credentials:
            return {}

        now = datetime.datetime.utcnow()
        six_seconds = datetime.timedelta(seconds=6)
        valid_until = (now + six_seconds).isoformat()
        # Append "Z" to indicate Zulu (=UTC) time.
        valid_until +=  "Z"

        return {'fake_role': '{"Code": "Success", "Expiration": "%s"}' % valid_until}
