from __future__ import print_function, absolute_import, division

import logging
import sys

import yamlreader


def _get_item_from_module(module_name, item_name):
    """Load classes/modules/functions/... from given config"""
    try:
        module = __import__(module_name, fromlist=[item_name])
        klass = getattr(module, item_name)
    except ImportError as error:
        message = 'Module "{modulename}" could not be loaded: {e}'
        raise Exception(message.format(
            modulename=module_name, e=error))
    except AttributeError as error:
        message = 'No item "{itemname}" in module "{modulename}": {e}'
        raise Exception(message.format(
            modulename=module_name,
            itemname=item_name,
            e=error))
    return klass


def levelname_to_integer(levelname):
    levelname = levelname.lower()
    level_translation = {'debug': logging.DEBUG, 'info': logging.INFO,
                         'warning': logging.WARNING, 'error': logging.ERROR}
    return level_translation[levelname]


def setup_logging(config):
    handler_config = config.get('logging_handler')
    levelname = config.get('log_level', 'warning')
    logger = logging.getLogger('alppaca')
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
    klass = _get_item_from_module(handler_config['module'],
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
