from datetime import datetime
from time import strptime
from functools import wraps
from time import time
import json
import logging
import pytz
import yaml


def init_logging(debug):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S',
                        level=level)

    return logging.getLogger(__name__)


def load_config(config_file):
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    return config


def convert_rfc3339_to_datetime(timestamp):
    return datetime(*strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")[0:6], tzinfo=pytz.utc)


def extract_min_expiration(credentials):
    return min([json.loads(value)['Expiration']
                for value in credentials.values()])


def total_seconds(timedelta):
    return (timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 10**6) / 10**6


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

