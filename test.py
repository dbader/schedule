import functools
import time
import schedule

foo = lambda: print("hi")
schedule.every(2).friday.do(foo)
schedule.run_pending()
