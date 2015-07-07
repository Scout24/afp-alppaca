import logging

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
