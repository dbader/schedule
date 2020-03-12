"""
Python job scheduling for humans.

github.com/dbader/schedule

An in-process scheduler for periodic jobs that uses the builder pattern
for configuration. Schedule lets you run Python functions (or any other
callable) periodically at pre-determined intervals using a simple,
human-friendly syntax.

Inspired by Addam Wiggins' article "Rethinking Cron" [1] and the
"clockwork" Ruby module [2][3].

Features:
    - A simple to use API for scheduling jobs.
    - Very lightweight and no external dependencies.
    - Excellent test coverage.
    - Tested on Python 2.7, 3.5, 3.6, 3.7 and 3.8

Usage:
    >>> import schedule
    >>> import time

    >>> def job(message='stuff'):
    >>>     print("I'm working on:", message)

    >>> schedule.every(10).minutes.do(job)
    >>> schedule.every(5).to(10).days.do(job)
    >>> schedule.every().hour.do(job, message='things')
    >>> schedule.every().day.at("10:30").do(job)

    >>> while True:
    >>>     schedule.run_pending()
    >>>     time.sleep(1)

[1] https://adam.herokuapp.com/past/2010/4/13/rethinking_cron/
[2] https://github.com/Rykian/clockwork
[3] https://adam.herokuapp.com/past/2010/6/30/replace_cron_with_clockwork/
"""
try:
    from collections.abc import Hashable
except ImportError:
    from collections import Hashable

from schedule.async_job import AsyncJob
from schedule.async_scheduler import AsyncScheduler
from schedule.job import *
from schedule.scheduler import *

# The following methods are shortcuts for not having to
# create a Scheduler instance:

#: Default :class:`Scheduler <Scheduler>` object
default_scheduler = Scheduler()

#: Default :class:`Jobs <Job>` list
jobs = default_scheduler.jobs  # todo: should this be a copy, e.g. jobs()?


def every(interval=1):
    """Calls :meth:`every <Scheduler.every>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    return default_scheduler.every(interval)


def run_pending():
    """Calls :meth:`run_pending <Scheduler.run_pending>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.run_pending()


def run_all(delay_seconds=0):
    """Calls :meth:`run_all <Scheduler.run_all>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.run_all(delay_seconds=delay_seconds)


def clear(tag=None):
    """Calls :meth:`clear <Scheduler.clear>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.clear(tag)


def cancel_job(job):
    """Calls :meth:`cancel_job <Scheduler.cancel_job>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.cancel_job(job)


def next_run():
    """Calls :meth:`next_run <Scheduler.next_run>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    return default_scheduler.next_run


def idle_seconds():
    """Calls :meth:`idle_seconds <Scheduler.idle_seconds>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    return default_scheduler.idle_seconds
