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
    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile()
        self.config = dict(DEFAULT_TEST_CONFIG)
        self.config['logging_handler']['args'] = [self.tmpfile.name]

    def _helper(self):
        with AlppacaIntegrationTest(self.config) as ait:
            try:
                ait.execute()
            except AssertionError as e:
                self.fail(e)

    def test_log_is_empty_when_log_level_error(self):
        self.config['log_level'] = 'error'

        self._helper()

        content = self.tmpfile.read()
        self.assertEqual(content, b'')

    def test_log_with_content_log_level_debug(self):
        self._helper()

        content = self.tmpfile.read()
        self.assertGreater(len(content), 0)

    def test_log_format_is_applied(self):
        self.config['log_format'] = 'foobar: hello world'

        self._helper()

        content = self.tmpfile.read()
        self.assertIn(b'foobar: hello world', content)


if __name__ == '__main__':
    unittest.main()
