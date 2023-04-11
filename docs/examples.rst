Examples
========

Eager to get started? This page gives a good introduction to Schedule.
It assumes you already have Schedule installed. If you do not, head over to :doc:`installation`.

Run a job every x minute
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import schedule
    import time

    def job():
        print("I'm working...")

    # Run job every 3 second/minute/hour/day/week,
    # Starting 3 second/minute/hour/day/week from now
    schedule.every(3).seconds.do(job)
    schedule.every(3).minutes.do(job)
    schedule.every(3).hours.do(job)
    schedule.every(3).days.do(job)
    schedule.every(3).weeks.do(job)

    # Run job every minute at the 23rd second
    schedule.every().minute.at(":23").do(job)

    # Run job every hour at the 42nd minute
    schedule.every().hour.at(":42").do(job)

    # Run jobs every 5th hour, 20 minutes and 30 seconds in.
    # If current time is 02:00, first execution is at 06:20:30
    schedule.every(5).hours.at("20:30").do(job)

    # Run job every day at specific HH:MM and next HH:MM:SS
    schedule.every().day.at("10:30").do(job)
    schedule.every().day.at("10:30:42").do(job)
    schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)

    # Run job on a specific day of the week
    schedule.every().monday.do(job)
    schedule.every().wednesday.at("13:15").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

Use a decorator to schedule a job
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``@repeat`` to schedule a function.
Pass it an interval using the same syntax as above while omitting the ``.do()``.

.. code-block:: python

    from schedule import every, repeat, run_pending
    import time

    @repeat(every(10).minutes)
    def job():
        print("I am a scheduled job")

    while True:
        run_pending()
        time.sleep(1)

The ``@repeat`` decorator does not work on non-static class methods.

Pass arguments to a job
~~~~~~~~~~~~~~~~~~~~~~~

``do()`` passes extra arguments to the job function

.. code-block:: python

    import schedule

    def greet(name):
        print('Hello', name)

    schedule.every(2).seconds.do(greet, name='Alice')
    schedule.every(4).seconds.do(greet, name='Bob')

    from schedule import every, repeat

    @repeat(every().second, "World")
    @repeat(every().day, "Mars")
    def hello(planet):
        print("Hello", planet)


Cancel a job
~~~~~~~~~~~~
To remove a job from the scheduler, use the ``schedule.cancel_job(job)`` method

.. code-block:: python

    import schedule

    def some_task():
        print('Hello world')

    job = schedule.every().day.at('22:30').do(some_task)
    schedule.cancel_job(job)


Run a job once
~~~~~~~~~~~~~~

Return ``schedule.CancelJob`` from a job to remove it from the scheduler.

.. code-block:: python

    import schedule
    import time

    def job_that_executes_once():
        # Do some work that only needs to happen once...
        return schedule.CancelJob

    schedule.every().day.at('22:30').do(job_that_executes_once)

    while True:
        schedule.run_pending()
        time.sleep(1)


Get all jobs
~~~~~~~~~~~~
To retrieve all jobs from the scheduler, use ``schedule.get_jobs()``

.. code-block:: python

    import schedule

    def hello():
        print('Hello world')

    schedule.every().second.do(hello)

    all_jobs = schedule.get_jobs()


Cancel all jobs
~~~~~~~~~~~~~~~
To remove all jobs from the scheduler, use ``schedule.clear()``

.. code-block:: python

    import schedule

    def greet(name):
        print('Hello {}'.format(name))

    schedule.every().second.do(greet)

    schedule.clear()


Get several jobs, filtered by tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can retrieve a group of jobs from the scheduler, selecting them by a unique identifier.

.. code-block:: python

    import schedule

    def greet(name):
        print('Hello {}'.format(name))

    schedule.every().day.do(greet, 'Andrea').tag('daily-tasks', 'friend')
    schedule.every().hour.do(greet, 'John').tag('hourly-tasks', 'friend')
    schedule.every().hour.do(greet, 'Monica').tag('hourly-tasks', 'customer')
    schedule.every().day.do(greet, 'Derek').tag('daily-tasks', 'guest')

    friends = schedule.get_jobs('friend')

Will return a list of every job tagged as ``friend``.


Cancel several jobs, filtered by tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can cancel the scheduling of a group of jobs selecting them by a unique identifier.

.. code-block:: python

    import schedule

    def greet(name):
        print('Hello {}'.format(name))

    schedule.every().day.do(greet, 'Andrea').tag('daily-tasks', 'friend')
    schedule.every().hour.do(greet, 'John').tag('hourly-tasks', 'friend')
    schedule.every().hour.do(greet, 'Monica').tag('hourly-tasks', 'customer')
    schedule.every().day.do(greet, 'Derek').tag('daily-tasks', 'guest')

    schedule.clear('daily-tasks')

Will prevent every job tagged as ``daily-tasks`` from running again.


Run a job at random intervals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def my_job():
        print('Foo')

    # Run every 5 to 10 seconds.
    schedule.every(5).to(10).seconds.do(my_job)

``every(A).to(B).seconds`` executes the job function every N seconds such that A <= N <= B.


Run a job until a certain time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import schedule
    from datetime import datetime, timedelta, time

    def job():
        print('Boo')

    # run job until a 18:30 today
    schedule.every(1).hours.until("18:30").do(job)

    # run job until a 2030-01-01 18:33 today
    schedule.every(1).hours.until("2030-01-01 18:33").do(job)

    # Schedule a job to run for the next 8 hours
    schedule.every(1).hours.until(timedelta(hours=8)).do(job)

    # Run my_job until today 11:33:42
    schedule.every(1).hours.until(time(11, 33, 42)).do(job)

    # run job until a specific datetime
    schedule.every(1).hours.until(datetime(2020, 5, 17, 11, 36, 20)).do(job)

The ``until`` method sets the jobs deadline. The job will not run after the deadline.

Time until the next execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use ``schedule.idle_seconds()`` to get the number of seconds until the next job is scheduled to run.
The returned value is negative if the next scheduled jobs was scheduled to run in the past.
Returns ``None`` if no jobs are scheduled.

.. code-block:: python

    import schedule
    import time

    def job():
        print('Hello')

    schedule.every(5).seconds.do(job)

    while 1:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        schedule.run_pending()


Run all jobs now, regardless of their scheduling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To run all jobs regardless if they are scheduled to run or not, use ``schedule.run_all()``.
Jobs are re-scheduled after finishing, just like they would if they were executed using ``run_pending()``.

.. code-block:: python

    import schedule

    def job_1():
        print('Foo')

    def job_2():
        print('Bar')

    schedule.every().monday.at("12:40").do(job_1)
    schedule.every().tuesday.at("16:40").do(job_2)

    schedule.run_all()

    # Add the delay_seconds argument to run the jobs with a number
    # of seconds delay in between.
    schedule.run_all(delay_seconds=10)
