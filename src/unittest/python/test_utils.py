from __future__ import print_function, absolute_import, unicode_literals, division

import datetime
from textwrap import dedent


class FixedDateTime(datetime.datetime):
    """ As unfortunately datetime.datetime.now can not be mocked, since it is
    an c-extension.  We use this derived class and override now.

    http://stackoverflow.com/questions/4481954/python-trying-to-mock-datetime-date-today-but-not-working

    """
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(1970, 01, 01, tzinfo=tz)

json_response = dedent("""
                {"Code": "Success",
                "AccessKeyId": "ASIAI",
                "SecretAccessKey": "oieDhF",
                "Token": "6jmePdXNehjPVt7CZ1WMkKrqB6zDc34d2vpLej",
                "Expiration": "2015-04-17T13:40:18Z",
                "Type": "AWS-HMAC"}
                """)
