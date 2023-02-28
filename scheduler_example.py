import datetime as dt
import time

import pause
from scheduler import Scheduler
from scheduler.trigger import Monday, Tuesday

def foo():
    print("foo",dt.datetime.now())
    time.sleep(5)

schedule = Scheduler()

schedule.cyclic(dt.timedelta(seconds=10), foo)

schedule.minutely(dt.time(second=15), foo)
schedule.hourly(dt.time(minute=30, second=15), foo)
schedule.daily(dt.time(hour=16, minute=30), foo)
schedule.weekly(Monday(), foo)
schedule.weekly(Monday(dt.time(hour=16, minute=30)), foo)

schedule.once(dt.timedelta(minutes=10), foo)
schedule.once(Tuesday(), foo)
schedule.once(dt.datetime(year=2022, month=2, day=15, minute=45), foo)

while True:
    schedule.exec_jobs()
    next_time = dt.datetime.now().replace(microsecond=0) + dt.timedelta(seconds=1)
    pause.until(next_time)