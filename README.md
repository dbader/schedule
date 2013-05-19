schedule
========

Python job scheduling for humans. Inspired by [Adam Wiggins'](https://github.com/adamwiggins) [clockwork](https://github.com/tomykaira/clockwork)

Installation
------------
```sh
$ pip install schedule
```

Usage
-----

```python
def job():
    print("I'm working...")

schedule.every(10).minutes.do(job)
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)

while 1:
    schedule.tick()
    time.sleep(1)
```

Meta
----------
Daniel Bader – mail@dbader.org

Distributed under the MIT license. See LICENSE.txt for more information.

https://github.com/dbader/schedule
