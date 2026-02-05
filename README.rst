`schedule <https://schedule.readthedocs.io/>`__
===============================================


.. image:: https://github.com/dbader/schedule/workflows/Tests/badge.svg
        :target: https://github.com/dbader/schedule/actions?query=workflow%3ATests+branch%3Amaster

.. image:: https://coveralls.io/repos/dbader/schedule/badge.svg?branch=master
        :target: https://coveralls.io/r/dbader/schedule

.. image:: https://img.shields.io/pypi/v/schedule.svg
        :target: https://pypi.python.org/pypi/schedule

Python job scheduling for humans. Run Python functions (or any other callable) periodically using a friendly syntax.

- A simple to use API for scheduling jobs, made for humans.
- In-process scheduler for periodic jobs. No extra processes needed!
- Very lightweight and no external dependencies.
- Excellent test coverage.
- Tested on Python and 3.7, 3.8, 3.9, 3.10, 3.11, 3.12

Usage
-----

.. code-block:: bash

    $ pip install schedule

.. code-block:: python

    import schedule
    import time

    def job():
        print("I'm working...")

    schedule.every(10).seconds.do(job)
    schedule.every(10).minutes.do(job)
    schedule.every().hour.do(job)
    schedule.every().day.at("10:30").do(job)
    schedule.every(5).to(10).minutes.do(job)
    schedule.every().monday.do(job)
    schedule.every().wednesday.at("13:15").do(job)
    schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)
    schedule.every().minute.at(":17").do(job)

    def job_with_argument(name):
        print(f"I am {name}")

    schedule.every(10).seconds.do(job_with_argument, name="Peter")

    while True:
        schedule.run_pending()
        time.sleep(1)

Project Structure
-----------------

The library consists of a single module:

- ``schedule/__init__.py``: 945 lines containing all scheduling logic (``Scheduler``, ``Job`` classes and module-level functions)
- ``test_schedule.py``: single test file covering the entire codebase

**Dependencies:**

- Core: none (standard library only)
- Optional: ``pytz`` (required only for timezone-aware scheduling via ``.at("HH:MM", "Timezone")``)

Install with timezone support:

.. code-block:: bash

    $ pip install schedule[timezone]

Key API Concepts
----------------

**Default Scheduler**

The module provides a default ``Scheduler`` instance. Functions like ``every()``, ``run_pending()``, ``clear()``, and ``get_jobs()`` operate on this shared instance.

.. code-block:: python

    import schedule

    schedule.every(10).seconds.do(lambda: print("tick"))
    schedule.run_pending()      # execute jobs that are due
    schedule.get_jobs()         # list all scheduled jobs
    schedule.clear()            # remove all jobs

**Job Tagging**

Jobs can be tagged for selective retrieval or cancellation.

.. code-block:: python

    schedule.every().day.do(send_report).tag("daily", "reports")
    schedule.every().hour.do(cleanup).tag("maintenance")

    schedule.get_jobs("reports")    # jobs tagged "reports"
    schedule.clear("maintenance")   # cancel jobs tagged "maintenance"

**Randomized Intervals with** ``.to()``

Run a job at random intervals within a range.

.. code-block:: python

    # Executes every N minutes where 5 <= N <= 10
    schedule.every(5).to(10).minutes.do(refresh_cache)

**Job Expiration with** ``.until()``

Schedule a job to stop running after a given time.

.. code-block:: python

    from datetime import datetime, timedelta

    # Stop after a specific datetime
    schedule.every(1).hour.do(task).until(datetime(2024, 12, 31, 23, 59))

    # Stop after a duration
    schedule.every(30).seconds.do(task).until(timedelta(hours=2))

    # Stop at a specific time today
    schedule.every(5).minutes.do(task).until("18:00")

**Decorator Syntax with** ``@repeat``

Define scheduled jobs using a decorator.

.. code-block:: python

    from schedule import every, repeat, run_pending

    @repeat(every(10).seconds)
    def heartbeat():
        print("alive")

    while True:
        run_pending()

Automated Tests
---------------

Tests are written using ``unittest`` from the Python standard library and are contained in a single file: ``test_schedule.py``. They verify the behavior of the public API (scheduling, execution, tagging, cancellation, timezone handling).

Run tests with the built-in runner:

.. code-block:: bash

    $ python -m unittest test_schedule

Or use ``pytest`` as an alternative runner (not required):

.. code-block:: bash

    $ pytest test_schedule.py

Documentation
-------------

Schedule's documentation lives at `schedule.readthedocs.io <https://schedule.readthedocs.io/>`_.


Meta
----

Daniel Bader - `@dbader_org <https://twitter.com/dbader_org>`_ - mail@dbader.org

Inspired by `Adam Wiggins' <https://github.com/adamwiggins>`_ article `"Rethinking Cron" <https://adam.herokuapp.com/past/2010/4/13/rethinking_cron/>`_ and the `clockwork <https://github.com/Rykian/clockwork>`_ Ruby module.

Distributed under the MIT license. See `LICENSE.txt <https://github.com/dbader/schedule/blob/master/LICENSE.txt>`_ for more information.

https://github.com/dbader/schedule
