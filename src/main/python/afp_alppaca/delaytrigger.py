from __future__ import print_function, absolute_import, unicode_literals, division

import datetime

from apscheduler.triggers.date import DateTrigger
import pytz


class DelayTrigger(DateTrigger):
    """ Trigger for events to be run in X seconds. """

    def __init__(self, seconds):
        if seconds >= 0:
            run_date = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=seconds)
        else:
            run_date = None

        super(DelayTrigger, self).__init__(run_date=run_date)

