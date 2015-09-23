from __future__ import print_function, absolute_import, unicode_literals, division

""" Compatability module for different Python versions. """

try:
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest
try:
    from ordereddict import OrderedDict
except ImportError:  # pragma: no cover
    from collections import OrderedDict
