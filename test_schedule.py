"""Unit tests for schedule.py"""
import datetime
import functools
import mock
import unittest

# Silence "missing docstring", "method could be a function",
# "class already defined", and "too many public methods" messages:
# pylint: disable-msg=R0201,C0111,E0102,R0904,R0901

import schedule
from schedule import every, ScheduleError, ScheduleValueError, IntervalError


def make_mock_job(name=None):
    job = mock.Mock()
    job.__name__ = name or 'job'
    return job


class mock_datetime(object):
    """
    Monkey-patch datetime for predictable results
    """
    def __init__(self, year, month, day, hour, minute, second=0):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def __enter__(self):
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(self.year, self.month, self.day)

            @classmethod
            def now(cls):
                return cls(self.year, self.month, self.day,
                           self.hour, self.minute, self.second)
        self.original_datetime = datetime.datetime
        datetime.datetime = MockDate

    def __exit__(self, *args, **kwargs):
        datetime.datetime = self.original_datetime


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        schedule.clear()

    def test_time_units(self):
        assert every().seconds.unit == 'seconds'
        assert every().minutes.unit == 'minutes'
        assert every().hours.unit == 'hours'
        assert every().days.unit == 'days'
        assert every().weeks.unit == 'weeks'

        job_instance = schedule.Job(interval=2)
        # without a context manager, it incorrectly raises an error because
        # it is not callable
        with self.assertRaises(IntervalError):
            job_instance.minute
        with self.assertRaises(IntervalError):
            job_instance.hour
        with self.assertRaises(IntervalError):
            job_instance.day
        with self.assertRaises(IntervalError):
            job_instance.week
        with self.assertRaises(IntervalError):
            job_instance.monday
        with self.assertRaises(IntervalError):
            job_instance.tuesday
        with self.assertRaises(IntervalError):
            job_instance.wednesday
        with self.assertRaises(IntervalError):
            job_instance.thursday
        with self.assertRaises(IntervalError):
            job_instance.friday
        with self.assertRaises(IntervalError):
            job_instance.saturday
        with self.assertRaises(IntervalError):
            job_instance.sunday

        # test an invalid unit
        job_instance.unit = "foo"
        self.assertRaises(ScheduleValueError, job_instance.at, "1:0:0")
        self.assertRaises(ScheduleValueError, job_instance._schedule_next_run)

        # test start day exists but unit is not 'weeks'
        job_instance.unit = "days"
        job_instance.start_day = 1
        self.assertRaises(ScheduleValueError, job_instance._schedule_next_run)

        # test weeks with an invalid start day
        job_instance.unit = "weeks"
        job_instance.start_day = "bar"
        self.assertRaises(ScheduleValueError, job_instance._schedule_next_run)

        # test a valid unit with invalid hours/minutes/seconds
        job_instance.unit = "days"
        self.assertRaises(ScheduleValueError, job_instance.at, "25:00:00")
        self.assertRaises(ScheduleValueError, job_instance.at, "00:61:00")
        self.assertRaises(ScheduleValueError, job_instance.at, "00:00:61")

        # test invalid time format
        self.assertRaises(ScheduleValueError, job_instance.at, "25:0:0")
        self.assertRaises(ScheduleValueError, job_instance.at, "0:61:0")
        self.assertRaises(ScheduleValueError, job_instance.at, "0:0:61")

        # test (very specific) seconds with unspecified start_day
        job_instance.unit = "seconds"
        job_instance.at_time = datetime.datetime.now()
        job_instance.start_day = None
        self.assertRaises(ScheduleValueError, job_instance._schedule_next_run)

        # test self.latest >= self.interval
        job_instance.latest = 1
        self.assertRaises(ScheduleError, job_instance._schedule_next_run)
        job_instance.latest = 3
        self.assertRaises(ScheduleError, job_instance._schedule_next_run)

    def test_singular_time_units_match_plural_units(self):
        assert every().second.unit == every().seconds.unit
        assert every().minute.unit == every().minutes.unit
        assert every().hour.unit == every().hours.unit
        assert every().day.unit == every().days.unit
        assert every().week.unit == every().weeks.unit

    def test_time_range(self):
        with mock_datetime(2014, 6, 28, 12, 0):
            mock_job = make_mock_job()

            # Choose a sample size large enough that it's unlikely the
            # same value will be chosen each time.
            minutes = set([
                every(5).to(30).minutes.do(mock_job).next_run.minute
                for i in range(100)
            ])

            assert len(minutes) > 1
            assert min(minutes) >= 5
            assert max(minutes) <= 30

    def test_time_range_repr(self):
        mock_job = make_mock_job()

        with mock_datetime(2014, 6, 28, 12, 0):
            job_repr = repr(every(5).to(30).minutes.do(mock_job))

        assert job_repr.startswith('Every 5 to 30 minutes do job()')

    def test_at_time(self):
        mock_job = make_mock_job()
        assert every().day.at('10:30').do(mock_job).next_run.hour == 10
        assert every().day.at('10:30').do(mock_job).next_run.minute == 30
        assert every().day.at('10:30:50').do(mock_job).next_run.second == 50

        self.assertRaises(ScheduleValueError, every().day.at, '2:30:000001')
        self.assertRaises(ScheduleValueError, every().day.at, '::2')
        self.assertRaises(ScheduleValueError, every().day.at, '.2')
        self.assertRaises(ScheduleValueError, every().day.at, '2')
        self.assertRaises(ScheduleValueError, every().day.at, ':2')
        self.assertRaises(ScheduleValueError, every().day.at, ' 2:30:00')
        self.assertRaises(ScheduleValueError, every().do, lambda: 0)
        self.assertRaises(TypeError, every().day.at, 2)

        # without a context manager, it incorrectly raises an error because
        # it is not callable
        with self.assertRaises(IntervalError):
            every(interval=2).second
        with self.assertRaises(IntervalError):
            every(interval=2).minute
        with self.assertRaises(IntervalError):
            every(interval=2).hour
        with self.assertRaises(IntervalError):
            every(interval=2).day
        with self.assertRaises(IntervalError):
            every(interval=2).week
        with self.assertRaises(IntervalError):
            every(interval=2).monday
        with self.assertRaises(IntervalError):
            every(interval=2).tuesday
        with self.assertRaises(IntervalError):
            every(interval=2).wednesday
        with self.assertRaises(IntervalError):
            every(interval=2).thursday
        with self.assertRaises(IntervalError):
            every(interval=2).friday
        with self.assertRaises(IntervalError):
            every(interval=2).saturday
        with self.assertRaises(IntervalError):
            every(interval=2).sunday

    def test_weekday_at_todady(self):
        mock_job = make_mock_job()

        # This date is a wednesday
        with mock_datetime(2020, 11, 25, 22, 38, 5):
            job = every().wednesday.at('22:38:10').do(mock_job)
            assert job.next_run.hour == 22
            assert job.next_run.minute == 38
            assert job.next_run.second == 10
            assert job.next_run.year == 2020
            assert job.next_run.month == 11
            assert job.next_run.day == 25

            job = every().wednesday.at('22:39').do(mock_job)
            assert job.next_run.hour == 22
            assert job.next_run.minute == 39
            assert job.next_run.second == 00
            assert job.next_run.year == 2020
            assert job.next_run.month == 11
            assert job.next_run.day == 25

    def test_at_time_hour(self):
        with mock_datetime(2010, 1, 6, 12, 20):
            mock_job = make_mock_job()
            assert every().hour.at(':30').do(mock_job).next_run.hour == 12
            assert every().hour.at(':30').do(mock_job).next_run.minute == 30
            assert every().hour.at(':30').do(mock_job).next_run.second == 0
            assert every().hour.at(':10').do(mock_job).next_run.hour == 13
            assert every().hour.at(':10').do(mock_job).next_run.minute == 10
            assert every().hour.at(':10').do(mock_job).next_run.second == 0
            assert every().hour.at(':00').do(mock_job).next_run.hour == 13
            assert every().hour.at(':00').do(mock_job).next_run.minute == 0
            assert every().hour.at(':00').do(mock_job).next_run.second == 0

            self.assertRaises(ScheduleValueError, every().hour.at, '2:30:00')
            self.assertRaises(ScheduleValueError, every().hour.at, '::2')
            self.assertRaises(ScheduleValueError, every().hour.at, '.2')
            self.assertRaises(ScheduleValueError, every().hour.at, '2')
            self.assertRaises(ScheduleValueError, every().hour.at, ' 2:30')
            self.assertRaises(ScheduleValueError, every().hour.at, "61:00")
            self.assertRaises(ScheduleValueError, every().hour.at, "00:61")
            self.assertRaises(ScheduleValueError, every().hour.at, "01:61")
            self.assertRaises(TypeError, every().hour.at, 2)

    def test_at_time_minute(self):
        with mock_datetime(2010, 1, 6, 12, 20, 30):
            mock_job = make_mock_job()
            assert every().minute.at(':40').do(mock_job).next_run.hour == 12
            assert every().minute.at(':40').do(mock_job).next_run.minute == 20
            assert every().minute.at(':40').do(mock_job).next_run.second == 40
            assert every().minute.at(':10').do(mock_job).next_run.hour == 12
            assert every().minute.at(':10').do(mock_job).next_run.minute == 21
            assert every().minute.at(':10').do(mock_job).next_run.second == 10

            self.assertRaises(ScheduleValueError, every().minute.at, '::2')
            self.assertRaises(ScheduleValueError, every().minute.at, '.2')
            self.assertRaises(ScheduleValueError, every().minute.at, '2')
            self.assertRaises(ScheduleValueError, every().minute.at, '2:30:00')
            self.assertRaises(ScheduleValueError, every().minute.at, '2:30')
            self.assertRaises(ScheduleValueError, every().minute.at, ' :30')
            self.assertRaises(TypeError, every().minute.at, 2)

    def test_next_run_time(self):
        with mock_datetime(2010, 1, 6, 12, 15):
            mock_job = make_mock_job()
            assert schedule.next_run() is None
            assert every().minute.do(mock_job).next_run.minute == 16
            assert every(5).minutes.do(mock_job).next_run.minute == 20
            assert every().hour.do(mock_job).next_run.hour == 13
            assert every().day.do(mock_job).next_run.day == 7
            assert every().day.at('09:00').do(mock_job).next_run.day == 7
            assert every().day.at('12:30').do(mock_job).next_run.day == 6
            assert every().week.do(mock_job).next_run.day == 13
            assert every().monday.do(mock_job).next_run.day == 11
            assert every().tuesday.do(mock_job).next_run.day == 12
            assert every().wednesday.do(mock_job).next_run.day == 13
            assert every().thursday.do(mock_job).next_run.day == 7
            assert every().friday.do(mock_job).next_run.day == 8
            assert every().saturday.do(mock_job).next_run.day == 9
            assert every().sunday.do(mock_job).next_run.day == 10

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
        assert s == ("Job(interval=1, unit=minutes, do=job_fun, "
                     "args=('foo',), kwargs={'bar': 23})")
        assert 'job_fun' in s
        assert 'foo' in s
        assert '{\'bar\': 23}' in s

    def test_to_repr(self):
        def job_fun():
            pass
        s = repr(every().minute.do(job_fun, 'foo', bar=23))
        assert s.startswith("Every 1 minute do job_fun('foo', bar=23) "
                            "(last run: [never], next run: ")
        assert 'job_fun' in s
        assert 'foo' in s
        assert 'bar=23' in s

        # test repr when at_time is not None
        s2 = repr(every().day.at("00:00").do(job_fun, 'foo', bar=23))
        assert s2.startswith(("Every 1 day at 00:00:00 do job_fun('foo', "
                              "bar=23) (last run: [never], next run: "))

    def test_to_string_lambda_job_func(self):
        assert len(str(every().minute.do(lambda: 1))) > 1
        assert len(str(every().day.at('10:30').do(lambda: 1))) > 1

    def test_to_string_functools_partial_job_func(self):
        def job_fun(arg):
            pass
        job_fun = functools.partial(job_fun, 'foo')
        job_repr = repr(every().minute.do(job_fun, bar=True, somekey=23))
        assert 'functools.partial' in job_repr
        assert 'bar=True' in job_repr
        assert 'somekey=23' in job_repr

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
        mock_job = make_mock_job()

        with mock_datetime(2010, 1, 6, 12, 15):
            every().minute.do(mock_job)
            every().hour.do(mock_job)
            every().day.do(mock_job)
            every().sunday.do(mock_job)
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 6, 12, 16):
            schedule.run_pending()
            assert mock_job.call_count == 1

        with mock_datetime(2010, 1, 6, 13, 16):
            mock_job.reset_mock()
            schedule.run_pending()
            assert mock_job.call_count == 2

        with mock_datetime(2010, 1, 7, 13, 16):
            mock_job.reset_mock()
            schedule.run_pending()
            assert mock_job.call_count == 3

        with mock_datetime(2010, 1, 10, 13, 16):
            mock_job.reset_mock()
            schedule.run_pending()
            assert mock_job.call_count == 4

    def test_run_every_weekday_at_specific_time_today(self):
        mock_job = make_mock_job()
        with mock_datetime(2010, 1, 6, 13, 16):
            every().wednesday.at('14:12').do(mock_job)
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 6, 14, 16):
            schedule.run_pending()
            assert mock_job.call_count == 1

    def test_run_every_weekday_at_specific_time_past_today(self):
        mock_job = make_mock_job()
        with mock_datetime(2010, 1, 6, 13, 16):
            every().wednesday.at('13:15').do(mock_job)
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 13, 13, 14):
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 13, 13, 16):
            schedule.run_pending()
            assert mock_job.call_count == 1

    def test_run_every_n_days_at_specific_time(self):
        mock_job = make_mock_job()
        with mock_datetime(2010, 1, 6, 11, 29):
            every(2).days.at('11:30').do(mock_job)
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 6, 11, 31):
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 7, 11, 31):
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 8, 11, 29):
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 8, 11, 31):
            schedule.run_pending()
            assert mock_job.call_count == 1

        with mock_datetime(2010, 1, 10, 11, 31):
            schedule.run_pending()
            assert mock_job.call_count == 2

    def test_next_run_property(self):
        original_datetime = datetime.datetime
        with mock_datetime(2010, 1, 6, 13, 16):
            hourly_job = make_mock_job('hourly')
            daily_job = make_mock_job('daily')
            every().day.do(daily_job)
            every().hour.do(hourly_job)
            assert len(schedule.jobs) == 2
            # Make sure the hourly job is first
            assert schedule.next_run() == original_datetime(2010, 1, 6, 14, 16)
            assert schedule.idle_seconds() == 60 * 60

    def test_cancel_job(self):
        def stop_job():
            return schedule.CancelJob
        mock_job = make_mock_job()

        every().second.do(stop_job)
        mj = every().second.do(mock_job)
        assert len(schedule.jobs) == 2

        schedule.run_all()
        assert len(schedule.jobs) == 1
        assert schedule.jobs[0] == mj

        schedule.cancel_job('Not a job')
        assert len(schedule.jobs) == 1
        schedule.default_scheduler.cancel_job('Not a job')
        assert len(schedule.jobs) == 1

        schedule.cancel_job(mj)
        assert len(schedule.jobs) == 0

    def test_cancel_jobs(self):
        def stop_job():
            return schedule.CancelJob

        every().second.do(stop_job)
        every().second.do(stop_job)
        every().second.do(stop_job)
        assert len(schedule.jobs) == 3

        schedule.run_all()
        assert len(schedule.jobs) == 0

    def test_tag_type_enforcement(self):
        job1 = every().second.do(make_mock_job(name='job1'))
        self.assertRaises(TypeError, job1.tag, {})
        self.assertRaises(TypeError, job1.tag, 1, 'a', [])
        job1.tag(0, 'a', True)
        assert len(job1.tags) == 3

    def test_clear_by_tag(self):
        every().second.do(make_mock_job(name='job1')).tag('tag1')
        every().second.do(make_mock_job(name='job2')).tag('tag1', 'tag2')
        every().second.do(make_mock_job(name='job3')).tag('tag3', 'tag3',
                                                          'tag3', 'tag2')
        assert len(schedule.jobs) == 3
        schedule.run_all()
        assert len(schedule.jobs) == 3
        schedule.clear('tag3')
        assert len(schedule.jobs) == 2
        schedule.clear('tag1')
        assert len(schedule.jobs) == 0
        every().second.do(make_mock_job(name='job1'))
        every().second.do(make_mock_job(name='job2'))
        every().second.do(make_mock_job(name='job3'))
        schedule.clear()
        assert len(schedule.jobs) == 0

    def test_misconfigured_job_wont_break_scheduler(self):
        """
        Ensure an interrupted job definition chain won't break
        the scheduler instance permanently.
        """
        scheduler = schedule.Scheduler()
        scheduler.every()
        scheduler.every(10).seconds
        scheduler.run_pending()
