from __future__ import print_function, absolute_import, division

from afp_alppaca.main import run_scheduler_and_webserver
from afp_alppaca.compat import unittest
from test_utils import AlppacaIntegrationTest


DEFAULT_TEST_CONFIG = {
    'ims_host': '127.0.0.1',
    'ims_port': 8080,
    'ims_protocol': 'http',
    'bind_ip': '127.0.0.1',
    'bind_port': 25772,
    'logging_handler': {
        'module': 'logging',
        'class': 'StreamHandler',
        'args': [],
        'kwargs': {}
    }
}


class RunAlppacaTests(unittest.TestCase):
    def _helper(self, config):
        with AlppacaIntegrationTest(config) as ait:
            try:
                ait.execute()
            except AssertionError as e:
                self.fail(e)

    def test_default_credentials(self):
        self._helper(DEFAULT_TEST_CONFIG)

    def test_should_use_custom_bind_ip_and_port(self):
        config = DEFAULT_TEST_CONFIG.copy()
        config['bind_port'] = 5001
        self._helper(config)


if __name__ == '__main__':
    unittest.main()
