"""Unit tests for schedule.py"""
import unittest
import mock
import datetime

# Silence "missing docstring", "method could be a function",
# "class already defined", and "too many public methods" messages:
# pylint: disable-msg=R0201,C0111,E0102,R0904,R0901

import schedule
from schedule import every


def make_mock_job(name=None):
    job = mock.Mock()
    job.__name__ = name or 'job'
    return job


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        schedule.clear()

    def test_time_units(self):
        assert every().seconds.unit == 'seconds'
        assert every().minutes.unit == 'minutes'
        assert every().hours.unit == 'hours'
        assert every().days.unit == 'days'
        assert every().weeks.unit == 'weeks'

    def test_singular_time_units_match_plural_units(self):
        assert every().second.unit == every().seconds.unit
        assert every().minute.unit == every().minutes.unit
        assert every().hour.unit == every().hours.unit
        assert every().day.unit == every().days.unit
        assert every().week.unit == every().weeks.unit

    def test_at_time(self):
        mock_job = make_mock_job()
        assert every().day.at('10:30').do(mock_job).next_run.hour == 10
        assert every().day.at('10:30').do(mock_job).next_run.minute == 30

    def test_next_run_time(self):
        # Monkey-patch datetime.datetime to get predictable (=testable) results
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 12, 15)
        original_datetime = datetime.datetime
        datetime.datetime = MockDate

        mock_job = make_mock_job()
        assert every().minute.do(mock_job).next_run.minute == 16
        assert every(5).minutes.do(mock_job).next_run.minute == 20
        assert every().hour.do(mock_job).next_run.hour == 13
        assert every().day.do(mock_job).next_run.day == 7
        assert every().day.at('09:00').do(mock_job).next_run.day == 7
        assert every().day.at('12:30').do(mock_job).next_run.day == 6
        assert every().week.do(mock_job).next_run.day == 13

        datetime.datetime = original_datetime

    def test_run_all(self):
        mock_job = make_mock_job()
        every().minute.do(mock_job)
        every().hour.do(mock_job)
        every().day.at('11:00').do(mock_job)
        schedule.run_all()
        assert mock_job.call_count == 3

    def test_job_func_args_are_passed_on(self):
        mock_job = make_mock_job()
        every().second.do(mock_job, 1, 2, 'three', foo=23, bar={})
        schedule.run_all()
        mock_job.assert_called_once_with(1, 2, 'three', foo=23, bar={})

    def test_to_string(self):
        def job_fun():
            pass
        s = str(every().minute.do(job_fun, 'foo', bar=23))
        assert 'job_fun' in s
        assert 'foo' in s
        assert 'bar=23' in s
        assert len(str(every().minute.do(lambda: 1))) > 1
        assert len(str(every().day.at("10:30").do(lambda: 1))) > 1

    def test_run_pending(self):
        """Check that run_pending() runs pending jobs.
        We do this by overriding datetime.datetime with mock objects
        that represent increasing system times.

        Please note that it is *intended behavior that run_pending() does not
        run missed jobs*. For example, if you've registered a job that
        should run every minute and you only call run_pending() in one hour
        increments then your job won't be run 60 times in between but
        only once.
        """
        # Monkey-patch datetime.datetime to get predictable (=testable) results
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 12, 15)
        original_datetime = datetime.datetime
        datetime.datetime = MockDate

        mock_job = make_mock_job()
        every().minute.do(mock_job)
        every().hour.do(mock_job)
        every().day.do(mock_job)

        schedule.run_pending()
        assert mock_job.call_count == 0

        # Minutely
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 12, 16)
        datetime.datetime = MockDate
        schedule.run_pending()
        assert mock_job.call_count == 1

        # Minutely, hourly
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 13, 16)
        datetime.datetime = MockDate

        mock_job.reset_mock()
        schedule.run_pending()
        assert mock_job.call_count == 2

        # Minutely, hourly, daily
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 7)

            @classmethod
            def now(cls):
                return cls(2010, 1, 7, 13, 16)
        datetime.datetime = MockDate

        mock_job.reset_mock()
        schedule.run_pending()
        assert mock_job.call_count == 3

        datetime.datetime = original_datetime

    def test_run_every_n_days_at_specific_time(self):
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 13, 16)
        original_datetime = datetime.datetime
        datetime.datetime = MockDate

        mock_job = make_mock_job()
        every(2).days.at("11:30").do(mock_job)

        schedule.run_pending()
        assert mock_job.call_count == 0

        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 7)

            @classmethod
            def now(cls):
                return cls(2010, 1, 7, 13, 16)
        datetime.datetime = MockDate

        schedule.run_pending()
        assert mock_job.call_count == 0

        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 8)

            @classmethod
            def now(cls):
                return cls(2010, 1, 8, 13, 16)
        datetime.datetime = MockDate

        schedule.run_pending()
        assert mock_job.call_count == 1

        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 10)

            @classmethod
            def now(cls):
                return cls(2010, 1, 10, 13, 16)
        datetime.datetime = MockDate

        schedule.run_pending()
        assert mock_job.call_count == 2

        datetime.datetime = original_datetime

    def test_next_run_property(self):
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 13, 16)
        original_datetime = datetime.datetime
        datetime.datetime = MockDate

        hourly_job = make_mock_job('hourly')
        daily_job = make_mock_job('daily')
        every().day.do(daily_job)
        every().hour.do(hourly_job)
        assert len(schedule.jobs) == 2
        # Make sure the hourly job is first
        assert schedule.next_run() == original_datetime(2010, 1, 6, 14, 16)
        assert schedule.idle_seconds() == 60 * 60

        datetime.datetime = original_datetime
