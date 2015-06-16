import logging
from functools import wraps
from time import time


def init_logging(debug):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S',
                        level=level)

    return logging.getLogger(__name__)


def timed(function):

    logger = logging.getLogger(__name__)

    @wraps(function)
    def wrapper(*args, **kwds):
        start = time()
        result = function(*args, **kwds)
        elapsed = time() - start
        logger.debug("{0} execution needed {1}s".format(function.__name__, round(elapsed, 3)))
        return result

    return wrapper