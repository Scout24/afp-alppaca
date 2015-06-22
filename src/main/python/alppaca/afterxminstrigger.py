import datetime
from apscheduler.triggers.date import DateTrigger


class AfterXMinsTrigger(DateTrigger):
    
    def __init__(self, minutes):
        run_date = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        super(AfterXMinsTrigger, self).__init__(run_date=run_date)