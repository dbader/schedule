import datetime
from unittest import mock

import pytest
import schedule


class Clock(datetime.datetime):
    current = datetime.datetime(2024, 1, 1)

    @classmethod
    def now(cls, tz=None):
        return cls.current


def fractional_jobs() -> list:
    scheduler = schedule.Scheduler()
    return [schedule.every(0.5), scheduler.every(0.5), schedule.Job(0.5)]


@pytest.mark.parametrize("unit", ["seconds", "minutes", "hours", "days", "weeks"])
def test_fractional_time_units(unit):
    scheduler = schedule.Scheduler()
    with mock.patch.object(schedule.datetime, "datetime", Clock):
        Clock.current = datetime.datetime(2024, 1, 1)
        job = getattr(scheduler.every(0.5), unit).do(lambda: None)
        assert job.next_run == Clock.current + datetime.timedelta(**{unit: 0.5})


def test_fractional_run_pending():
    scheduler = schedule.Scheduler()
    callback = mock.Mock()
    with mock.patch.object(schedule.datetime, "datetime", Clock):
        Clock.current = datetime.datetime(2024, 1, 1)
        job = scheduler.every(0.5).seconds.do(callback)
        Clock.current += datetime.timedelta(milliseconds=499)
        scheduler.run_pending()
        callback.assert_not_called()
        Clock.current += datetime.timedelta(milliseconds=1)
        scheduler.run_pending()
        callback.assert_called_once_with()
        assert job.next_run == Clock.current + datetime.timedelta(seconds=0.5)
        scheduler.run_pending()
        callback.assert_called_once_with()


def test_fractional_constructors():
    assert [job.interval for job in fractional_jobs()] == [0.5, 0.5, 0.5]


def test_integer_random_intervals_unchanged():
    with mock.patch.object(schedule.random, "randint", return_value=3) as randint:
        schedule.Scheduler().every(2).to(4).seconds.do(lambda: None)
        randint.assert_called_once_with(2, 4)
