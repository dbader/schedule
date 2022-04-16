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
When scheduling jobs with relative time (that is when not using ``.at()``), daylight saving time (DST) is **not** taken into account.
A job that is set to run every 4 hours might execute after 3 realtime hours when DST goes into effect.
This is because schedule is timezone-unaware for relative times.

However, when using ``.at()``, DST **is** handed correctly: the job will always run at (or close after) the set timestamp.
A job scheduled during a moment that is skipped, the job will execute after the clock is moved.
For example, a job is scheduled ``.at("02:30")``, clock moves from ``02:00`` to ``03:00``, the job will run at ``03:00``.

Example
~~~~~~~
Let's say we are in ``Europe/Berlin`` and local datetime is ``2022 march 20, 10:00:00``.
At the moment daylight saving time is not in effect in Berlin (UTC+1).

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
