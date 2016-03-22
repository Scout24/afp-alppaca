from __future__ import print_function, absolute_import, unicode_literals, division

import argparse
import sys

from afp_alppaca.assume_role import AssumedRoleCredentialsProvider
from afp_alppaca.ims_interface import IMSCredentialsProvider
from afp_alppaca.scheduler import Scheduler
from afp_alppaca.webapp import WebApp
from afp_alppaca.util import setup_logging, load_config
from afp_alppaca.compat import OrderedDict
from succubus import Daemon

def run_webapp(config, logger, credentials):
    bind_ip = config.get('bind_ip', '127.0.0.1')
    bind_port = config.get('bind_port', '25772')
    logger.debug("Starting webserver on %s:%s", bind_ip, bind_port)

    webapp = WebApp(credentials)
    webapp.run(host=bind_ip, port=bind_port, quiet=True)


class AlppacaDaemon(Daemon):
    def run(self):
        try:
            # Credentials is a shared object that connects the scheduler and the
            # bottle_app. The scheduler writes into it and the bottle_app reads
            # from it.
            self.credentials = OrderedDict()

            self.launch_scheduler()
            run_webapp(self.config, self.logger, self.credentials)
        except Exception:
            self.logger.exception("Error in Alppaca")
        finally:
            self.logger.info("Alppaca shutting down...")

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-c', '--config', help="Alppaca YAML config directory", type=str,
            default='/etc/alppaca')

        return parser.parse_args()

    def load_configuration(self):
        args = self.parse_arguments()
        self.config = load_config(args.config)
        self.setup_logging()

    def setup_logging(self):
        try:
            self.logger = setup_logging(self.config)
        except Exception:
            print("Could not setup logging with config '{0}'".format(self.config),
                  file=sys.stderr)
            raise
        else:
            self.logger.debug("Alppaca logging was set up")

    def get_credentials_provider(self):
        # initialize the credentials provider
        ims_host_port = '%s:%s' % (self.config['ims_host'], self.config['ims_port'])
        ims_protocol = self.config.get('ims_protocol', 'https')
        self.logger.info("Will get credentials from '%s' using '%s'",
                    ims_host_port, ims_protocol)
        credentials_provider = IMSCredentialsProvider(ims_host_port,
                                                      ims_protocol=ims_protocol)

        role_to_assume = self.config.get('assume_role')
        if role_to_assume:
            self.logger.info("Option assume_role set to '%s'", role_to_assume)
            credentials_provider = AssumedRoleCredentialsProvider(
                credentials_provider,
                role_to_assume,
                self.config.get('aws_proxy_host'),
                self.config.get('aws_proxy_port'),
                self.config.get('aws_region')
            )
        return credentials_provider

    def launch_scheduler(self):
        credentials_provider = self.get_credentials_provider()
        scheduler = Scheduler(self.credentials, credentials_provider)
        scheduler.refresh_credentials()
