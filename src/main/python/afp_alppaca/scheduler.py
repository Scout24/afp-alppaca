from __future__ import print_function, absolute_import, unicode_literals, division

import datetime
import isodate
import json
import logging
import six
import time
from random import uniform

from afp_alppaca.ims_interface import NoRolesFoundException
import pytz


class Scheduler(object):
    """ Scheduler for refreshing credentials.

        By default it will fetch the credentials and then schedule itself to
        update them based on the expiration date. Some randomness is involved
        to avoid collisions. In case of failure to fetch credentials a back-off
        and safety behaviour is initiated.
    """
    def __init__(self, credentials, credentials_provider):
        self.logger = logging.getLogger(__name__)
        self.credentials = credentials
        self.credentials_provider = credentials_provider
        self.backoff = None

    def do_backoff(self, factor=1.5, max_interval=10):
        """ Perform back-off and safety. """
        if self.backoff is None:
            self.logger.debug("Initializing back-off and safety behaviour "
                              "with factor %s and a max interval %s",
                              factor, max_interval)
            self.backoff = backoff_refresh_generator(factor, max_interval)
        refresh_delta = six.next(self.backoff)
        return refresh_delta

    def refresh_credentials(self):
        while True:
            try:
                next_sleep = self._refresh_credentials()
            except Exception:
                self.logger.exception("Unhandled error while refreshing credentials:")
                next_sleep = 120
            self.logger.debug("Sleeping %s seconds before next credential "
                              "refresh...", next_sleep)
            time.sleep(next_sleep)

    def _refresh_credentials(self):
        """ Refresh credentials and schedule next refresh."""
        self.logger.debug("about to fetch credentials")
        new_credentials = None
        factor, max_interval = 1.5, 10

        try:
            new_credentials = self.credentials_provider.get_credentials_for_all_roles()
        except NoRolesFoundException:
            factor, max_interval = 3, 300
        except Exception:
            self.logger.exception("Error in credential provider:")

        if new_credentials:
            return self.update_credentials(new_credentials)
        else:
            self.logger.info("No credentials found!")
            return self.do_backoff(factor=factor, max_interval=max_interval)

    def update_credentials(self, new_credentials):
        """ Update credentials and retrigger refresh """
        self.credentials.update(new_credentials)
        self.logger.info("Got credentials")
        self.logger.debug("Credential cache: %s", self.credentials)
        refresh_delta = self.extract_refresh_delta()
        if refresh_delta < 0:
            self.logger.warn("Expiration date is in the past, entering backoff.")
            return self.do_backoff()
        else:
            if self.backoff is not None:
                self.backoff = None
                self.logger.debug("Exiting backoff state.")
            refresh_delta = self.sample_new_refresh_delta(refresh_delta)
            return refresh_delta

    def extract_refresh_delta(self):
        """ Return shortest expiration time in seconds. """
        expiration = isodate.parse_datetime(extract_min_expiration(self.credentials))
        refresh_delta = total_seconds(expiration - datetime.datetime.now(tz=pytz.utc))

        self.logger.debug("Extracted expiration: %s %s (in %s seconds)",
                          expiration, expiration.tzname(), refresh_delta)
        return refresh_delta

    def sample_new_refresh_delta(self, refresh_delta):
        """ Sample a new refresh delta. """
        refresh_delta = int(uniform(refresh_delta * .5, refresh_delta * .9))
        return refresh_delta

def backoff_refresh_generator(factor, max_interval):
    """ Generate refresh deltas when in back-off and safety mode. """
    count = factor
    while True:
        if count < max_interval:
            yield count
            count *= factor
        else:
            yield max_interval


def extract_min_expiration(credentials):
    """ The smallest expiration date of all the available credentials. """
    return min([json.loads(value)['Expiration']
                for value in credentials.values()])


def total_seconds(timedelta):
    """ Convert timedelta to seconds as an integer. """
    delta_seconds = timedelta.seconds + timedelta.days * 24 * 3600
    return (timedelta.microseconds + delta_seconds * 10 ** 6) // 10 ** 6
