import pause

import schedule
import datetime as dt


def greet(name):
    print('\n Hello', name, dt.datetime.now())
    pause.seconds(1)


# schedule.every(2).seconds.do(greet, name='Alice')
# schedule.every(4).seconds.do(greet, name='Bob')
#
from schedule import every, repeat

scheduler1 = schedule.Scheduler(start_time_based=False)


@repeat(scheduler1.every(5).seconds, "World")
@repeat(every().day, "Mars")
def hello(planet):
    print("\n Hello1", planet, dt.datetime.now())
    pause.seconds(2)


while True:
    scheduler1.run_pending()
    next_time = dt.datetime.now().replace(microsecond=0) + dt.timedelta(seconds=1)
    pause.until(next_time)