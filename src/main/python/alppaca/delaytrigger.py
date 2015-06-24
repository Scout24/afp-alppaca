import datetime
from apscheduler.triggers.date import DateTrigger


class DelayTrigger(DateTrigger):
    
    def __init__(self, seconds):
        if seconds > 0:
            run_date = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        else:
            run_date = None
            
        super(DelayTrigger, self).__init__(run_date=run_date)