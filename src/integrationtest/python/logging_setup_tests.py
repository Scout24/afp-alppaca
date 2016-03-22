from __future__ import print_function, absolute_import, division

import tempfile

from afp_alppaca.compat import unittest
from test_utils import AlppacaIntegrationTest


DEFAULT_TEST_CONFIG = {
    'ims_host': '127.0.0.1',
    'ims_port': 8080,
    'ims_protocol': 'http',
    'bind_ip': '127.0.0.1',
    'bind_port': 25772,
    'log_level': 'DEBUG',
    'logging_handler': {
        'module': 'logging',
        'class': 'FileHandler',
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

    def test_log_is_empty_when_log_level_error(self):
        tmpfile = tempfile.NamedTemporaryFile()
        DEFAULT_TEST_CONFIG['logging_handler']['args'] = [tmpfile.name]
        DEFAULT_TEST_CONFIG['log_level'] = 'error'

        self._helper(DEFAULT_TEST_CONFIG)

        content = tmpfile.read()
        self.assertEqual(content, b'')

    def test_log_with_content_log_level_debug(self):
        tmpfile = tempfile.NamedTemporaryFile()
        DEFAULT_TEST_CONFIG['logging_handler']['args'] = [tmpfile.name]
        DEFAULT_TEST_CONFIG['log_level'] = 'debug'

        self._helper(DEFAULT_TEST_CONFIG)

        content = tmpfile.read()
        self.assertGreater(len(content), 0)

    def test_log_format_is_applied(self):
        tmpfile = tempfile.NamedTemporaryFile()
        DEFAULT_TEST_CONFIG['logging_handler']['args'] = [tmpfile.name]
        DEFAULT_TEST_CONFIG['log_level'] = 'debug'
        DEFAULT_TEST_CONFIG['log_format'] = 'foobar: hello world'

        self._helper(DEFAULT_TEST_CONFIG)

        content = tmpfile.read()
        self.assertIn(b'foobar: hello world', content)


if __name__ == '__main__':
    unittest.main()
