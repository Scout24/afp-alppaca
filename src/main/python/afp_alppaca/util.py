from __future__ import print_function, absolute_import, division

import logging
import sys
import yamlreader
from pils import get_item_from_module, levelname_to_integer


def setup_logging(config):
    handler_config = config.get('logging_handler')
    levelname = config.get('log_level', 'warning')
    logger = logging.getLogger()
    if logger.handlers:
        # Was already initialized, nothing to do.
        return logger
    logger.setLevel(levelname_to_integer(levelname))
    default_config = {
        'module': 'logging.handlers',
        'class': 'SysLogHandler',
        'args': [],
        'kwargs': {'address': '/dev/log'}}
    handler_config = handler_config or default_config
    klass = get_item_from_module(handler_config['module'],
                                  handler_config['class'])
    args = handler_config.get('args', ())
    kwargs = handler_config.get('kwargs', {})
    try:
        handler = klass(*args, **kwargs)
    except Exception as exc:
        message = ("Could not instantiate logging handler class '{klass}' "
                   "with args '{args}', kwargs '{kwargs}': {exc}")
        raise Exception(message.format(klass=klass, args=args,
                                       kwargs=kwargs, exc=exc))

    log_format = config.get('log_format', 'alppaca: [%(levelname)s] %(message)s')
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def load_config(config_dir):
    try:
        return yamlreader.yaml_load(config_dir)
    except Exception:
        print("Could not load configuration from '{0}'".format(
            config_dir), file=sys.stderr)
        raise
