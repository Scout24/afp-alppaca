from alppaca.main import run_scheduler_and_webserver
from alppaca.server_mock import MockIms
from concurrent import futures
import requests
import time


def run_api_server_mock():
    MockIms().run()


def run_alppaca():
    run_scheduler_and_webserver('../resources/alppaca_test_config.yaml')


def test_alppaca_returns_given_role():
    response = requests.get('http://localhost:5000/latest/meta-data/iam/security-credentials/')
    print "Response was: " + response.content
    assert(response.content == 'test_role')


if __name__ == '__main__':
    executor = futures.ProcessPoolExecutor(max_workers=2)
    mock_job = executor.submit(run_api_server_mock)
    alppaca_job = executor.submit(run_alppaca)
    time.sleep(2)
    test_alppaca_returns_given_role()
