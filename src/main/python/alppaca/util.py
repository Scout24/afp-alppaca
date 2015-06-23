import logging
import numbers
import random

import yaml
# from functools import wraps
# from time import time


def init_logging(debug):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S',
                        level=level)

    return logging.getLogger(__name__)


def get_random_prime_wait_interval(min_value=1, max_value=100):
    while True:
        rand = random.randrange(min_value, max_value)
        if is_prime(rand):
            return rand
        else:
            continue


def is_prime(rand):
    if rand <= 3:
        return rand >= 2
    if rand % 2 == 0 or rand % 3 == 0:
        return False
    for i in range(5, int(rand ** 0.5) + 1, 6):
        if rand % i == 0 or rand % (i + 2) == 0:
            return False
    return True


def load_config(config_file):
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    return config



# def timed(function):
#
#     logger = logging.getLogger(__name__)
#
#     @wraps(function)
#     def wrapper(*args, **kwds):
#         start = time()
#         result = function(*args, **kwds)
#         elapsed = time() - start
#         logger.debug("{0} execution needed {1}s".format(function.__name__, round(elapsed, 3)))
#         return result
#
#     return wrapper