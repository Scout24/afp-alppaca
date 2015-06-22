from unittest import TestCase

from alppaca.util import get_random_prime_wait_interval, is_prime


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


def _check_number_is_prime(number):
    if number == 2 or number == 3:
        return True
    if number % 2 == 0 or number < 2:
        return False
    for i in range(3, int(number**0.5) + 1, 2):   # only odd numbers
        if number % i == 0:
            return False
    return True