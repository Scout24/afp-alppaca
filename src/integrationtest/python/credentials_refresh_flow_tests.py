from alppaca.main import run_scheduler_and_webserver
from alppaca.server_mock import MockIms
from concurrent import futures


def run_api_server_mock():
    MockIms().run()


def run_alppaca():
    run_scheduler_and_webserver('../resources/alppaca_test_config.yaml')


if __name__ == '__main__':
    executor = futures.ProcessPoolExecutor(max_workers=1)
    future = executor.submit(run_api_server_mock)

    run_alppaca()
