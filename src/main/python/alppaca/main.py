from __future__ import print_function, absolute_import, unicode_literals, division

import sys

from alppaca.assume_role import AssumedRoleCredentialsProvider
from alppaca.ims_interface import IMSCredentialsProvider
from alppaca.scheduler import Scheduler
from alppaca.webapp import WebApp
from alppaca.util import setup_logging
from alppaca.compat import OrderedDict


def run_scheduler_and_webserver(config):
    logging_config = None
    try:
        logger = setup_logging(config)
    except Exception:
        print("Could not setup logging with config '{0}'".format(
            logging_config), file=sys.stderr)
        raise
    try:
        # Credentials is a shared object that connects the scheduler and the
        # bottle_app. The scheduler writes into it and the bottle_app reads
        # from it.
        credentials = OrderedDict()
        # initialize the credentials provider
        ims_host_port = '%s:%s' % (config['ims_host'], config['ims_port'])
        ims_protocol = config.get('ims_protocol', 'https')
        credentials_provider = IMSCredentialsProvider(ims_host_port, ims_protocol=ims_protocol)

        role_to_assume = config.get('assume_role')
        if role_to_assume:
            credentials_provider = AssumedRoleCredentialsProvider(
                credentials_provider,
                role_to_assume,
                config.get('aws_proxy_host'),
                config.get('aws_proxy_port')
            )

        Scheduler(credentials, credentials_provider).refresh_credentials()
        # initialize and run the web app
        bind_ip = config.get('bind_ip', '127.0.0.1')
        bind_port = config.get('bind_port', '25772')
        webapp = WebApp(credentials)
        webapp.run(host=bind_ip, port=bind_port)
    except Exception:
        logger.exception("Cannot start Alppaca")
