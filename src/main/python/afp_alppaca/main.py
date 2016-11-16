from __future__ import print_function, absolute_import, unicode_literals, division

import argparse
import signal
import sys
import threading
from six.moves.http_client import HTTPConnection

from afp_alppaca.assume_role import AssumedRoleCredentialsProvider
from afp_alppaca.ims_interface import IMSCredentialsProvider
from afp_alppaca.scheduler import Scheduler
from afp_alppaca.util import setup_logging, load_config, redirect_print_to_log
from afp_alppaca.compat import OrderedDict
from succubus import Daemon


def sigterm_handler(*args):
    raise SystemExit("SIGTERM was received")


class AlppacaDaemon(Daemon):
    def run(self):
        self.logger.warn("Alppaca starting.")
        try:
            # Handle SIGTERM by raising SystemExit to make the "finally:" work.
            signal.signal(signal.SIGTERM, sigterm_handler)

            redirect_print_to_log(self.logger)

            # Credentials is a shared object that connects the scheduler and the
            # bottle_app. The scheduler writes into it and the bottle_app reads
            # from it.
            self.credentials = OrderedDict()

            self.launch_scheduler()
            self.run_webapp()
        except Exception:
            self.logger.exception("Error in Alppaca")
        finally:
            self.logger.warn("Alppaca shutting down.")

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

    def run_webapp(self):
        bind_ip = self.config.get('bind_ip', '127.0.0.1')
        bind_port = self.config.get('bind_port', '25772')
        self.logger.debug("Starting webserver on %s:%s", bind_ip, bind_port)

        # Bottle creates internal shortcuts for writing to STDOUT/STDERR.
        # Since we replace STDOUT/STDERR with our own versions, bottle needs
        # to be imported _after_ we replace things.
        from afp_alppaca.webapp import WebApp
        webapp = WebApp(self.credentials)
        webapp.run(host=bind_ip, port=bind_port, quiet=False)

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

        scheduler_thread = threading.Thread(target=scheduler.refresh_credentials)
        scheduler_thread.daemon = True
        scheduler_thread.start()

    def status(self):
        succubus_status = super(AlppacaDaemon, self).status()
        if succubus_status != 0:
            return succubus_status

        conn = HTTPConnection('169.254.169.254', timeout=0.1)
        try:
            conn.request("GET", "/")
            conn.getresponse()
        except Exception:
            print("Error: alppaca is not reachable via IP 169.254.169.254.")
            return 3
        else:
            return 0
