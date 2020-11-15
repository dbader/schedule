Logging
=======

To receive logs from Schedule, set the root logging level to at least ``INFO``.

.. code-block:: python

    import schedule
    import logging

    logging.basicConfig(level=logging.INFO)

    def job():
        print("Hello, Logs")

    schedule.every().second.do(job)

    schedule.run_all()

This will result in the following log messages:

.. code-block:: text

    INFO:schedule:Running *all* 1 jobs with 0s delay inbetween
    INFO:schedule:Running job Job(interval=1, unit=seconds, do=job, args=(), kwargs={})
    Hello, Logs


If you want to disable the schedule logs, while still receiving logs from other loggers, configure the ``schedule`` logger:

.. code-block:: python

    import logging

    # Only show ERROR logs of the scheduler
    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging.ERROR)


Customize logging
-----------------
The easiest way to add reusable logging to jobs is to implement a decorator that handles logging.
As an example, below code adds the ``print_elapsed_time`` decorator:

.. code-block:: python

    import functools
    import time
    import schedule

    # This decorator can be applied to any job function to
    # log the elapsed time of each job
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
