from __future__ import print_function, absolute_import, division

from alppaca.main import run_scheduler_and_webserver
from alppaca.server_mock import MockIms
from alppaca.compat import unittest
from multiprocessing import Process
import requests
import time
import sys


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


class AlppacaIntegrationTest(object):
    def __init__(self, config):
        self.config = config
        self.mock_job = Process(target=self.run_api_server_mock)
        self.alppaca_job = Process(target=self.run_alppaca)

    def __enter__(self):
        self.mock_job.start()
        self.alppaca_job.start()
        return self

    def __exit__(self, *args):
        self.mock_job.terminate()
        self.alppaca_job.terminate()

    def run_alppaca(self):
        run_scheduler_and_webserver(self.config)

    def run_api_server_mock(self):
        MockIms().run()

    def test_alppaca_returns_given_role(self):
        url = 'http://{host}:{port}/latest/meta-data/iam/security-credentials/'.format(
            host=self.config['bind_ip'], port=self.config['bind_port'])
        response = requests.get(url)

        assert response.status_code == 200, \
            "Response status code should be 200, was: '{0}'".format(response.status_code)
        assert(response.text == 'test_role'), \
            "Response text should be 'test_role', was: '{0}'".format(response.text)

    def execute(self):
        time.sleep(2)
        self.test_alppaca_returns_given_role()

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
