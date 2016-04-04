from __future__ import print_function, absolute_import, division

import os
import requests
import signal
import time
from multiprocessing import Process

from afp_alppaca.main import AlppacaDaemon
from afp_alppaca.server_mock import MockIms


class AlppacaIntegrationTest(object):
    def __init__(self, config):
        self.config = config
        self.mock_job = Process(target=self.run_api_server_mock)
        self.alppaca_job = Process(target=self.run_alppaca)

    def __enter__(self):
        self.mock_job.start()
        # Ensure the mock IMS fully(!) up and running before starting Alppaca.
        # Otherwise, Alppaca will see the failure and start its backoff
        # behaviour.
        time.sleep(0.5)
        self.alppaca_job.start()
        time.sleep(0.5)
        return self

    def __exit__(self, *args):
        self.mock_job.terminate()
        self.alppaca_job.terminate()

        self.mock_job.join(10)
        self.alppaca_job.join(10)

        mock_alive = self.mock_job.is_alive()
        if mock_alive:
            os.kill(self.mock_job.pid, signal.SIGKILL)

        alppaca_alive = self.alppaca_job.is_alive()
        if alppaca_alive:
            os.kill(self.alppaca_job.pid, signal.SIGKILL)

        if mock_alive or alppaca_alive:
            raise Exception("Processe(s) that ignored SIGTERM: "
                            "API mock server: %s  Alppaca: %s" % (
                            mock_alive, alppaca_alive))

    def run_alppaca(self):
        daemon = AlppacaDaemon(pid_file="not used")
        daemon.config = self.config
        daemon.setup_logging()
        daemon.run()

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
        self.test_alppaca_returns_given_role()
