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

scheduler = schedule.Scheduler()  # start_time_based=False)


@repeat(scheduler.every(13).seconds, "World")
@repeat(scheduler.every(7).seconds, "Mars")
@repeat(every().day, "Mars")
def hello(planet):
    print("\n Hello1", planet, dt.datetime.now())
    # pause.seconds(2)


# scheduler1.jobs


while True:
    scheduler.run_pending()
    print(scheduler.next_run)
    pause.until(scheduler.get_next_run())