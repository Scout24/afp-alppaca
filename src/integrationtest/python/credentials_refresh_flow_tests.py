from alppaca.main import run_scheduler_and_webserver
from alppaca.server_mock import MockIms
from multiprocessing import Process
import requests
import time
import sys


TEST_CONFIG = {
    'ims_host': '127.0.0.1',
    'ims_port': 8080,
    'ims_protocol': 'http'
}


def run_api_server_mock():
    MockIms().run()


def run_alppaca():
    run_scheduler_and_webserver(TEST_CONFIG)


def test_alppaca_returns_given_role():
    response = requests.get('http://localhost:5000/latest/meta-data/iam/security-credentials/')

    assert response.status_code == 200, \
        "Response status code should be 200, was: '{0}'".format(response.status_code)
    assert(response.content == 'test_role'), \
        "Response content should be 'test_role', was: '{0}'".format(response.content)


if __name__ == '__main__':
    mock_job = Process(target=run_api_server_mock)
    alppaca_job = Process(target=run_alppaca)

    mock_job.start()
    alppaca_job.start()

    try:
        time.sleep(2)
        test_alppaca_returns_given_role()
        sys.exit(0)
    except AssertionError as e:
        print "Test failed: {0}".format(e)
        sys.exit(1)
    finally:
        mock_job.terminate()
        alppaca_job.terminate()
