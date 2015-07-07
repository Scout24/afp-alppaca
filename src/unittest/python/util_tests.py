from unittest import TestCase
import datetime
import pytz

from alppaca.util import convert_rfc3339_to_datetime, extract_min_expiration


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

    def test_should_raise_exception_on_empty_credentials(self):
        input_ = {}
        self.assertRaises(ValueError, extract_min_expiration, input_)


class ConvertToDatetimeTest(TestCase):

    def test(self):
        input_ = "1970-01-01T00:00:00Z"
        expected = datetime.datetime(1970, 01, 01, 00, 00, 00, tzinfo=pytz.utc)
        received = convert_rfc3339_to_datetime(input_)
        self.assertEqual(expected, received)


