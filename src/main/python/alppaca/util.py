import logging

import yaml


def setup_logging(handler_config):
    logger = logging.getLogger('alppaca')
    if logger.handlers:
        # Was already initialized, nothing to do.
        return logger
    logger.setLevel(logging.DEBUG)
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
    except Exception, exc:
        message = ("Could not instantiate logging handler class '{klass}' "
                   "with args '{args}', kwargs '{kwargs}': {exc}")
        raise Exception(message.format(klass=klass, args=args,
                                       kwargs=kwargs, exc=exc))
    logger.addHandler(handler)
    return logger


def load_config(config_file):
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    return config
