from __future__ import print_function, absolute_import, division

import logging
import mock
import os
import shutil
import tempfile

from afp_alppaca.compat import unittest
from afp_alppaca.util import load_config, create_logging_handler, StdoutToLog


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_load_config_good_case(self):
        config_file_name = os.path.join(self.tmpdir, "config.yaml")
        with open(config_file_name, 'w') as config_file:
            config_file.write('the_answer: 42')

        loaded_config = load_config(self.tmpdir)

        self.assertEqual(loaded_config, {'the_answer': 42})

    def test_load_config_reports_config_dir_name(self):
        config_file_name = os.path.join(self.tmpdir, "broken_config.yaml")
        with open(config_file_name, 'w') as config_file:
            config_file.write('too: many: colons: in: one: line')

        # If loading fails, the exception string must contain the confdir name.
        self.assertRaisesRegexp(Exception, self.tmpdir,
                                load_config, self.tmpdir)

    def test_create_logging_handler_good_case(self):
        log_file_name = os.path.join(self.tmpdir, "unittest.log")
        handler_config = {
            'module': 'logging',
            'class': 'FileHandler',
            'args': [log_file_name],
            'kwargs': {}
        }

        handler = create_logging_handler(handler_config)

        expected_class = logging.FileHandler
        self.assertIsInstance(handler, expected_class)
        self.assertTrue(os.path.exists(log_file_name))

    def test_stdout_to_log(self):
        mock_logger = mock.Mock()
        out_to_log = StdoutToLog(mock_logger)
        message = "Hello, world!"

        out_to_log.write(message)

        mock_logger.warn.assert_called_with(message)
