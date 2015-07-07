import datetime


class FixedDateTime(datetime.datetime):
    """ As unfortunately datetime.datetime.now can not be mocked, since it is
    an c-extension.  We use this derived class and override now.

    http://stackoverflow.com/questions/4481954/python-trying-to-mock-datetime-date-today-but-not-working

    """
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime(1970, 01, 01, tzinfo=tz)
