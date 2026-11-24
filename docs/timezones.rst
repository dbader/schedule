Timezone & Daylight Saving Time
===============================

Timezone in .at()
~~~~~~~~~~~~~~~~~

Schedule supports setting the job execution time in another timezone using the ``.at`` method.

**To work with timezones** `pytz <https://pypi.org/project/pytz/>`_ **must be installed!** Get it:

.. code-block:: bash

    pip install pytz

Timezones are only available in the ``.at`` function, like so:

.. code-block:: python

    # Pass a timezone as a string
    schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)

    # Pass an pytz timezone object
    from pytz import timezone
    schedule.every().friday.at("12:42", timezone("Africa/Lagos")).do(job)

Schedule uses the timezone to calculate the next runtime in local time.
All datetimes inside the library are stored `naive <https://docs.python.org/3/library/datetime.html>`_.
This causes the ``next_run`` and ``last_run`` to always be in Pythons local timezone.

Daylight Saving Time
~~~~~~~~~~~~~~~~~~~~
Jobs that repeat every N seconds, minutes or hours count **real elapsed time**, also across clock-changes.
For example, a job that is set to run every 4 hours runs 4 realtime hours later, even when DST starts or ends in between.
Its ``next_run`` (in naive local time) therefore shifts by one hour on the wall clock.
When DST ends and the clock repeats an hour, these jobs keep running during the repeated hour.
The ``fold`` attribute of ``next_run`` tells which of the two repeated times is meant.

Daily and weekly jobs (``.day``, ``.monday``, ...) that do not specify a timezone use naive local times
to calculate the next run, so they stay at the same wall-clock time.

But when passing a timezone to ``.at()``, DST **is** taken into account.
The job will run at the specified time, even when the clock changes.

Example clock moves forward:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When a job is scheduled in the gap that occurs when the clock moves forward, the job is scheduled after the gap.

A job is scheduled ``.at("02:30", "Europe/Berlin")``.
When the clock moves from ``02:00`` to ``03:00``, the job will run once at ``03:30``.
The day after it will return to normal and run at ``02:30``.

A job is scheduled ``.at("01:00", "Europe/London")``.
When the clock moves from ``01:00`` to ``02:00``, the job will run once at ``02:00``.

Example clock moves backwards:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A job is scheduled ``.at("02:30", "Europe/Berlin")``.
When the clock moves from ``02:00`` to ``03:00``, the job will run once at ``02:30``.
It will run only at the first time the clock hits ``02:30``, but not the second time.
The day after, it will return to normal and run at ``02:30``.

Example scheduling across timezones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Let's say we are in ``Europe/Berlin`` and local datetime is ``2022 march 20, 10:00:00``.
At this moment daylight saving time is not in effect in Berlin (UTC+1).

We schedule a job to run every day at 10:30:00 in America/New_York.
At this time, daylight saving time is in effect in New York (UTC-4).

.. code-block:: python

    s = every().day.at("10:30", "America/New_York").do(job)

Because of the 5 hour time difference between Berlin and New York the job should effectively run at ``15:30:00``.
So the next run in Berlin time is ``2022 march 20, 15:30:00``:

.. code-block:: python

    print(s.next_run)
    # 2022-03-20 15:30:00

    print(repr(s))
    # Every 1 day at 10:30:00 do job() (last run: [never], next run: 2022-03-20 15:30:00)
