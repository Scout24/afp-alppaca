from unittest import TestCase
from mock import Mock
import datetime
import pytz

from alppaca.util import get_random_prime_wait_interval, is_prime, convert_rfc3339_to_datetime, extract_min_expiration, exponential_retry


class GetRandomPrimeNumber(TestCase):

    def test_get_first_prime_number(self):
        result = get_random_prime_wait_interval(1, 99)
        self.assertTrue(_check_number_is_prime(result))

    def test_get_first_prime_number_without_range(self):
        result = get_random_prime_wait_interval()
        self.assertTrue(_check_number_is_prime(result))

    def test_is_bad_prime_with_1(self):
        self.assertFalse(is_prime(1))

    def test_is_good_prime_with_2(self):
        self.assertTrue(is_prime(2))

    def test_is_bad_prime_with_4(self):
        self.assertFalse(is_prime(4))

    def test_is_bad_prime_with_91(self):
        self.assertFalse(is_prime(91))


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


class ConvertToDatetimeTest(TestCase):

    def test(self):
        input_ = "1970-01-01T00:00:00Z"
        expected = datetime.datetime(1970, 01, 01, 00, 00, 00, tzinfo=pytz.utc)
        received = convert_rfc3339_to_datetime(input_)
        self.assertEqual(expected, received)


class ExponentialRetryTests(TestCase):

    @exponential_retry
    def test_method(self, param):
        param('foo')

    def test_is_executed_once_on_success(self):
        mock = Mock()
        self.test_method(mock)
        mock.assert_called_once_with('foo')

    def test_is_executed_with_exception_is_retried_until_successful(self):
        mock = Mock()
        mock.side_effect = [Exception, 'foo']
        self.test_method(mock)
        mock.assert_called_with('foo')
        self.assertEqual(mock.call_count, 2)

    def test_raises_exception_if_retries_exhausted(self):
        mock = Mock()
        mock.side_effect = [Exception]
        self.test_method(mock)
        self.assertEqual(mock.call_count, 3)
        # TODO: Test for exception


def _check_number_is_prime(number):
    if number == 2 or number == 3:
        return True
    if number % 2 == 0 or number < 2:
        return False
    for i in range(3, int(number**0.5) + 1, 2):   # only odd numbers
        if number % i == 0:
            return False
    return True

