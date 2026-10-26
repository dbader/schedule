Logging
=======

Schedule logs messages to the Python logger named ``schedule`` at ``DEBUG`` level.
To receive logs from Schedule, set the logging level to ``DEBUG``.

.. code-block:: python

    import schedule
    import logging

    logging.basicConfig()
    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging.DEBUG)

    def job():
        print("Hello, Logs")

    schedule.every().second.do(job)

    schedule.run_all()

    schedule.clear()

This will result in the following log messages:

.. code-block:: text

    DEBUG:schedule:Running *all* 1 jobs with 0s delay in between
    DEBUG:schedule:Running job Job(interval=1, unit=seconds, do=job, args=(), kwargs={})
    Hello, Logs
    DEBUG:schedule:Deleting *all* jobs


Customize logging
-----------------
The easiest way to add reusable logging to jobs is to implement a decorator that handles logging.
As an example, below code adds the ``print_elapsed_time`` decorator:

.. code-block:: python

    import functools
    import time
    import schedule

    # This decorator can be applied to any job function to log the elapsed time of each job
    def print_elapsed_time(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_timestamp = time.time()
            print('LOG: Running job "%s"' % func.__name__)
            result = func(*args, **kwargs)
            print('LOG: Job "%s" completed in %d seconds' % (func.__name__, time.time() - start_timestamp))
            return result

        return wrapper


    @print_elapsed_time
    def job():
        print('Hello, Logs')
        time.sleep(5)

    schedule.every().second.do(job)

    schedule.run_all()

This outputs:

.. code-block:: text

    LOG: Running job "job"
    Hello, Logs
    LOG: Job "job" completed in 5 seconds


Hide sensitive job arguments
----------------------------

Schedule's debug messages include job arguments and keyword arguments. If these
contain passwords or tokens, use a custom job representation that omits them.
Override both ``__str__`` (used by Schedule's logs) and ``__repr__`` (used when
inspecting jobs), then have a scheduler create that job type:

.. code-block:: python

    import logging
    import schedule

    class PrivateJob(schedule.Job):
        def __str__(self):
            return (
                "Job(interval={!r}, unit={!r}, args=<hidden>, kwargs=<hidden>, "
                "last_run={!r}, next_run={!r})"
            ).format(self.interval, self.unit, self.last_run, self.next_run)

        __repr__ = __str__

    class PrivateScheduler(schedule.Scheduler):
        def every(self, interval=1):
            return PrivateJob(interval, self)

    def refresh_data(username, password):
        # Use the credentials here without logging them.
        print("Refreshing data")

    logging.basicConfig(level=logging.DEBUG)
    scheduler = PrivateScheduler()
    job = scheduler.every(10).minutes.do(
        refresh_data, "example-user", password="example-password"
    )
    scheduler.run_all()
    scheduler.cancel_job(job)

The job still receives its original arguments, but running and cancelling it
logs ``args=<hidden>, kwargs=<hidden>`` along with its interval and run times.
The callable's representation is also omitted, since it can contain sensitive
values. Register jobs through this scheduler rather than the module-level
``schedule.every()`` to use the custom representation.

This only changes job representations. Avoid secrets in job tags, application
log messages, or exception messages; those are not hidden by this example.
