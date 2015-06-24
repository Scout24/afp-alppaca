import datetime

from mock import Mock, patch
import pytz
from unittest import TestCase
from alppaca.scheduler import Scheduler


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