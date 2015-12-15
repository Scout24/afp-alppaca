from __future__ import print_function, absolute_import, unicode_literals, division

import logging

from afp_alppaca.util import levelname_to_integer
from afp_alppaca.compat import unittest


class TestUtil(unittest.TestCase):
    def test_levelname_to_integer_knows_all_loglevels(self):
        translated_level = levelname_to_integer('debug')
        self.assertEqual(translated_level, logging.DEBUG)
        translated_level = levelname_to_integer('info')
        self.assertEqual(translated_level, logging.INFO)
        translated_level = levelname_to_integer('warning')
        self.assertEqual(translated_level, logging.WARNING)
        translated_level = levelname_to_integer('error')
        self.assertEqual(translated_level, logging.ERROR)

    def test_case_insensitive_input_levelname_to_integer(self):
        translated_level = levelname_to_integer('DeBuG')
        self.assertEqual(translated_level, logging.DEBUG)
