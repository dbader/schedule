"""Unit tests for schedule.py"""

import datetime
import functools
from unittest import mock, TestCase
import os
import time

# Silence "missing docstring", "method could be a function",
# "class already defined", and "too many public methods" messages:
# pylint: disable-msg=R0201,C0111,E0102,R0904,R0901

import schedule
from schedule import (
    every,
    repeat,
    ScheduleError,
    ScheduleValueError,
    IntervalError,
)

# POSIX TZ string format
TZ_BERLIN = "CET-1CEST,M3.5.0,M10.5.0/3"
TZ_AUCKLAND = "NZST-12NZDT,M9.5.0,M4.1.0/3"
TZ_CHATHAM = "<+1245>-12:45<+1345>,M9.5.0/2:45,M4.1.0/3:45"
TZ_UTC = "UTC0"

# Set timezone to Europe/Berlin (CEST) to ensure global reproducibility
os.environ["TZ"] = TZ_BERLIN
time.tzset()


def make_mock_job(name=None):
    job = mock.Mock()
    job.__name__ = name or "job"
    return job


class mock_datetime:
    """
    Monkey-patch datetime for predictable results
    """

    def __init__(self, year, month, day, hour, minute, second=0, zone=None, fold=0):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.zone = zone
        self.fold = fold
        self.original_datetime = None
        self.original_zone = None

    def __enter__(self):
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(self.year, self.month, self.day)

            @classmethod
            def now(cls, tz=None):
                mock_date = cls(
                    self.year,
                    self.month,
                    self.day,
                    self.hour,
                    self.minute,
                    self.second,
                    fold=self.fold,
                )
                if tz:
                    return mock_date.astimezone(tz)
                return mock_date

        self.original_datetime = datetime.datetime
        datetime.datetime = MockDate

        self.original_zone = os.environ.get("TZ")
        if self.zone:
            os.environ["TZ"] = self.zone
            time.tzset()

        return MockDate(
            self.year, self.month, self.day, self.hour, self.minute, self.second
        )

    def __exit__(self, *args, **kwargs):
        datetime.datetime = self.original_datetime
        if self.original_zone:
            os.environ["TZ"] = self.original_zone
            time.tzset()


class SchedulerTests(TestCase):
    def setUp(self):
        schedule.clear()

    def make_tz_mock_job(self, name=None):
        try:
            import pytz
        except ModuleNotFoundError:
            self.skipTest("pytz unavailable")
            return
        return make_mock_job(name)

    def test_time_units(self):
        assert every().seconds.unit == "seconds"
        assert every().minutes.unit == "minutes"
        assert every().hours.unit == "hours"
        assert every().days.unit == "days"
        assert every().weeks.unit == "weeks"

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
        with self.assertRaisesRegex(
            IntervalError,
            (
                r"Scheduling \.monday\(\) jobs is only allowed for weekly jobs\. "
                r"Using \.monday\(\) on a job scheduled to run every 2 or more "
                r"weeks is not supported\."
            ),
        ):
            job_instance.monday
        with self.assertRaisesRegex(
            IntervalError,
            (
                r"Scheduling \.tuesday\(\) jobs is only allowed for weekly jobs\. "
                r"Using \.tuesday\(\) on a job scheduled to run every 2 or more "
                r"weeks is not supported\."
            ),
        ):
            job_instance.tuesday
        with self.assertRaisesRegex(
            IntervalError,
            (
                r"Scheduling \.wednesday\(\) jobs is only allowed for weekly jobs\. "
                r"Using \.wednesday\(\) on a job scheduled to run every 2 or more "
                r"weeks is not supported\."
            ),
        ):
            job_instance.wednesday
        with self.assertRaisesRegex(
            IntervalError,
            (
                r"Scheduling \.thursday\(\) jobs is only allowed for weekly jobs\. "
                r"Using \.thursday\(\) on a job scheduled to run every 2 or more "
                r"weeks is not supported\."
            ),
        ):
            job_instance.thursday
        with self.assertRaisesRegex(
            IntervalError,
            (
                r"Scheduling \.friday\(\) jobs is only allowed for weekly jobs\. "
                r"Using \.friday\(\) on a job scheduled to run every 2 or more "
                r"weeks is not supported\."
            ),
        ):
            job_instance.friday
        with self.assertRaisesRegex(
            IntervalError,
            (
                r"Scheduling \.saturday\(\) jobs is only allowed for weekly jobs\. "
                r"Using \.saturday\(\) on a job scheduled to run every 2 or more "
                r"weeks is not supported\."
            ),
        ):
            job_instance.saturday
        with self.assertRaisesRegex(
            IntervalError,
            (
                r"Scheduling \.sunday\(\) jobs is only allowed for weekly jobs\. "
                r"Using \.sunday\(\) on a job scheduled to run every 2 or more "
                r"weeks is not supported\."
            ),
        ):
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

        # test self.latest >= self.interval
        job_instance.latest = 1
        self.assertRaises(ScheduleError, job_instance._schedule_next_run)
        job_instance.latest = 3
        self.assertRaises(ScheduleError, job_instance._schedule_next_run)

    def test_next_run_with_tag(self):
        with mock_datetime(2014, 6, 28, 12, 0):
            job1 = every(5).seconds.do(make_mock_job(name="job1")).tag("tag1")
            job2 = every(2).hours.do(make_mock_job(name="job2")).tag("tag1", "tag2")
            job3 = (
                every(1)
                .minutes.do(make_mock_job(name="job3"))
                .tag("tag1", "tag3", "tag2")
            )
            assert schedule.next_run("tag1") == job1.next_run
            assert schedule.default_scheduler.get_next_run("tag2") == job3.next_run
            assert schedule.next_run("tag3") == job3.next_run
            assert schedule.next_run("tag4") is None

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
            minutes = set(
                [
                    every(5).to(30).minutes.do(mock_job).next_run.minute
                    for i in range(100)
                ]
            )

            assert len(minutes) > 1
            assert min(minutes) >= 5
            assert max(minutes) <= 30

    def test_time_range_repr(self):
        mock_job = make_mock_job()

        with mock_datetime(2014, 6, 28, 12, 0):
            job_repr = repr(every(5).to(30).minutes.do(mock_job))

        assert job_repr.startswith("Every 5 to 30 minutes do job()")

    def test_at_time(self):
        mock_job = make_mock_job()
        assert every().day.at("10:30").do(mock_job).next_run.hour == 10
        assert every().day.at("10:30").do(mock_job).next_run.minute == 30
        assert every().day.at("20:59").do(mock_job).next_run.minute == 59
        assert every().day.at("10:30:50").do(mock_job).next_run.second == 50

        self.assertRaises(ScheduleValueError, every().day.at, "2:30:000001")
        self.assertRaises(ScheduleValueError, every().day.at, "::2")
        self.assertRaises(ScheduleValueError, every().day.at, ".2")
        self.assertRaises(ScheduleValueError, every().day.at, "2")
        self.assertRaises(ScheduleValueError, every().day.at, ":2")
        self.assertRaises(ScheduleValueError, every().day.at, " 2:30:00")
        self.assertRaises(ScheduleValueError, every().day.at, "59:59")
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

    def test_until_time(self):
        mock_job = make_mock_job()
        # Check argument parsing
        with mock_datetime(2020, 1, 1, 10, 0, 0) as m:
            assert every().day.until(datetime.datetime(3000, 1, 1, 20, 30)).do(
                mock_job
            ).cancel_after == datetime.datetime(3000, 1, 1, 20, 30, 0)
            assert every().day.until(datetime.datetime(3000, 1, 1, 20, 30, 50)).do(
                mock_job
            ).cancel_after == datetime.datetime(3000, 1, 1, 20, 30, 50)
            assert every().day.until(datetime.time(12, 30)).do(
                mock_job
            ).cancel_after == m.replace(hour=12, minute=30, second=0, microsecond=0)
            assert every().day.until(datetime.time(12, 30, 50)).do(
                mock_job
            ).cancel_after == m.replace(hour=12, minute=30, second=50, microsecond=0)

            assert every().day.until(
                datetime.timedelta(days=40, hours=5, minutes=12, seconds=42)
            ).do(mock_job).cancel_after == datetime.datetime(2020, 2, 10, 15, 12, 42)

            assert every().day.until("10:30").do(mock_job).cancel_after == m.replace(
                hour=10, minute=30, second=0, microsecond=0
            )
            assert every().day.until("10:30:50").do(mock_job).cancel_after == m.replace(
                hour=10, minute=30, second=50, microsecond=0
            )
            assert every().day.until("3000-01-01 10:30").do(
                mock_job
            ).cancel_after == datetime.datetime(3000, 1, 1, 10, 30, 0)
            assert every().day.until("3000-01-01 10:30:50").do(
                mock_job
            ).cancel_after == datetime.datetime(3000, 1, 1, 10, 30, 50)
            assert every().day.until(datetime.datetime(3000, 1, 1, 10, 30, 50)).do(
                mock_job
            ).cancel_after == datetime.datetime(3000, 1, 1, 10, 30, 50)

        # Invalid argument types
        self.assertRaises(TypeError, every().day.until, 123)
        self.assertRaises(ScheduleValueError, every().day.until, "123")
        self.assertRaises(ScheduleValueError, every().day.until, "01-01-3000")

        # Using .until() with moments in the passed
        self.assertRaises(
            ScheduleValueError,
            every().day.until,
            datetime.datetime(2019, 12, 31, 23, 59),
        )
        self.assertRaises(
            ScheduleValueError, every().day.until, datetime.timedelta(minutes=-1)
        )
        one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        self.assertRaises(ScheduleValueError, every().day.until, one_hour_ago)

        # Unschedule job after next_run passes the deadline
        schedule.clear()
        with mock_datetime(2020, 1, 1, 11, 35, 10):
            mock_job.reset_mock()
            every(5).seconds.until(datetime.time(11, 35, 20)).do(mock_job)
            with mock_datetime(2020, 1, 1, 11, 35, 15):
                schedule.run_pending()
                assert mock_job.call_count == 1
                assert len(schedule.jobs) == 1
            with mock_datetime(2020, 1, 1, 11, 35, 20):
                schedule.run_all()
                assert mock_job.call_count == 2
                assert len(schedule.jobs) == 0

        # Unschedule job because current execution time has passed deadline
        schedule.clear()
        with mock_datetime(2020, 1, 1, 11, 35, 10):
            mock_job.reset_mock()
            every(5).seconds.until(datetime.time(11, 35, 20)).do(mock_job)
            with mock_datetime(2020, 1, 1, 11, 35, 50):
                schedule.run_pending()
                assert mock_job.call_count == 0
                assert len(schedule.jobs) == 0

    def test_weekday_at_todady(self):
        mock_job = make_mock_job()

        # This date is a wednesday
        with mock_datetime(2020, 11, 25, 22, 38, 5):
            job = every().wednesday.at("22:38:10").do(mock_job)
            assert job.next_run.hour == 22
            assert job.next_run.minute == 38
            assert job.next_run.second == 10
            assert job.next_run.year == 2020
            assert job.next_run.month == 11
            assert job.next_run.day == 25

            job = every().wednesday.at("22:39").do(mock_job)
            assert job.next_run.hour == 22
            assert job.next_run.minute == 39
            assert job.next_run.second == 00
            assert job.next_run.year == 2020
            assert job.next_run.month == 11
            assert job.next_run.day == 25

    def test_at_time_hour(self):
        with mock_datetime(2010, 1, 6, 12, 20):
            mock_job = make_mock_job()
            assert every().hour.at(":30").do(mock_job).next_run.hour == 12
            assert every().hour.at(":30").do(mock_job).next_run.minute == 30
            assert every().hour.at(":30").do(mock_job).next_run.second == 0
            assert every().hour.at(":10").do(mock_job).next_run.hour == 13
            assert every().hour.at(":10").do(mock_job).next_run.minute == 10
            assert every().hour.at(":10").do(mock_job).next_run.second == 0
            assert every().hour.at(":00").do(mock_job).next_run.hour == 13
            assert every().hour.at(":00").do(mock_job).next_run.minute == 0
            assert every().hour.at(":00").do(mock_job).next_run.second == 0

            self.assertRaises(ScheduleValueError, every().hour.at, "2:30:00")
            self.assertRaises(ScheduleValueError, every().hour.at, "::2")
            self.assertRaises(ScheduleValueError, every().hour.at, ".2")
            self.assertRaises(ScheduleValueError, every().hour.at, "2")
            self.assertRaises(ScheduleValueError, every().hour.at, " 2:30")
            self.assertRaises(ScheduleValueError, every().hour.at, "61:00")
            self.assertRaises(ScheduleValueError, every().hour.at, "00:61")
            self.assertRaises(ScheduleValueError, every().hour.at, "01:61")
            self.assertRaises(TypeError, every().hour.at, 2)

            # test the 'MM:SS' format
            assert every().hour.at("30:05").do(mock_job).next_run.hour == 12
            assert every().hour.at("30:05").do(mock_job).next_run.minute == 30
            assert every().hour.at("30:05").do(mock_job).next_run.second == 5
            assert every().hour.at("10:25").do(mock_job).next_run.hour == 13
            assert every().hour.at("10:25").do(mock_job).next_run.minute == 10
            assert every().hour.at("10:25").do(mock_job).next_run.second == 25
            assert every().hour.at("00:40").do(mock_job).next_run.hour == 13
            assert every().hour.at("00:40").do(mock_job).next_run.minute == 0
            assert every().hour.at("00:40").do(mock_job).next_run.second == 40

    def test_at_time_minute(self):
        with mock_datetime(2010, 1, 6, 12, 20, 30):
            mock_job = make_mock_job()
            assert every().minute.at(":40").do(mock_job).next_run.hour == 12
            assert every().minute.at(":40").do(mock_job).next_run.minute == 20
            assert every().minute.at(":40").do(mock_job).next_run.second == 40
            assert every().minute.at(":10").do(mock_job).next_run.hour == 12
            assert every().minute.at(":10").do(mock_job).next_run.minute == 21
            assert every().minute.at(":10").do(mock_job).next_run.second == 10

            self.assertRaises(ScheduleValueError, every().minute.at, "::2")
            self.assertRaises(ScheduleValueError, every().minute.at, ".2")
            self.assertRaises(ScheduleValueError, every().minute.at, "2")
            self.assertRaises(ScheduleValueError, every().minute.at, "2:30:00")
            self.assertRaises(ScheduleValueError, every().minute.at, "2:30")
            self.assertRaises(ScheduleValueError, every().minute.at, " :30")
            self.assertRaises(TypeError, every().minute.at, 2)

    def test_next_run_time(self):
        with mock_datetime(2010, 1, 6, 12, 15):
            mock_job = make_mock_job()
            assert schedule.next_run() is None
            assert every().minute.do(mock_job).next_run.minute == 16
            assert every(5).minutes.do(mock_job).next_run.minute == 20
            assert every().hour.do(mock_job).next_run.hour == 13
            assert every().day.do(mock_job).next_run.day == 7
            assert every().day.at("09:00").do(mock_job).next_run.day == 7
            assert every().day.at("12:30").do(mock_job).next_run.day == 6
            assert every().week.do(mock_job).next_run.day == 13
            assert every().monday.do(mock_job).next_run.day == 11
            assert every().tuesday.do(mock_job).next_run.day == 12
            assert every().wednesday.do(mock_job).next_run.day == 13
            assert every().thursday.do(mock_job).next_run.day == 7
            assert every().friday.do(mock_job).next_run.day == 8
            assert every().saturday.do(mock_job).next_run.day == 9
            assert every().sunday.do(mock_job).next_run.day == 10
            assert (
                every().minute.until(datetime.time(12, 17)).do(mock_job).next_run.minute
                == 16
            )

    def test_next_run_time_day_end(self):
        mock_job = make_mock_job()
        # At day 1, schedule job to run at daily 23:30
        with mock_datetime(2010, 12, 1, 23, 0, 0):
            job = every().day.at("23:30").do(mock_job)
            # first occurrence same day
            assert job.next_run.day == 1
            assert job.next_run.hour == 23

        # Running the job 01:00 on day 2, afterwards the job should be
        # scheduled at 23:30 the same day. This simulates a job that started
        # on day 1 at 23:30 and took 1,5 hours to finish
        with mock_datetime(2010, 12, 2, 1, 0, 0):
            job.run()
            assert job.next_run.day == 2
            assert job.next_run.hour == 23

        # Run the job at 23:30 on day 2, afterwards the job should be
        # scheduled at 23:30 the next day
        with mock_datetime(2010, 12, 2, 23, 30, 0):
            job.run()
            assert job.next_run.day == 3
            assert job.next_run.hour == 23

    def test_next_run_time_hour_end(self):
        try:
            import pytz
        except ModuleNotFoundError:
            self.skipTest("pytz unavailable")

        self.tst_next_run_time_hour_end(None, 0)

    def test_next_run_time_hour_end_london(self):
        try:
            import pytz
        except ModuleNotFoundError:
            self.skipTest("pytz unavailable")

        self.tst_next_run_time_hour_end("Europe/London", 0)

    def test_next_run_time_hour_end_katmandu(self):
        try:
            import pytz
        except ModuleNotFoundError:
            self.skipTest("pytz unavailable")

        # 12:00 in Berlin is 15:45 in Kathmandu
        # this test schedules runs at :10 minutes, so job runs at
        # 16:10 in Kathmandu, which is 13:25 in Berlin
        # in local time we don't run at :10, but at :25, offset of 15 minutes
        self.tst_next_run_time_hour_end("Asia/Kathmandu", 15)

    def tst_next_run_time_hour_end(self, tz, offsetMinutes):
        mock_job = make_mock_job()

        # So a job scheduled to run at :10 in Kathmandu, runs always 25 minutes
        with mock_datetime(2010, 10, 10, 12, 0, 0):
            job = every().hour.at(":10", tz).do(mock_job)
            assert job.next_run.hour == 12
            assert job.next_run.minute == 10 + offsetMinutes

        with mock_datetime(2010, 10, 10, 13, 0, 0):
            job.run()
            assert job.next_run.hour == 13
            assert job.next_run.minute == 10 + offsetMinutes

        with mock_datetime(2010, 10, 10, 13, 30, 0):
            job.run()
            assert job.next_run.hour == 14
            assert job.next_run.minute == 10 + offsetMinutes

    def test_next_run_time_minute_end(self):
        self.tst_next_run_time_minute_end(None)

    def test_next_run_time_minute_end_london(self):
        try:
            import pytz
        except ModuleNotFoundError:
            self.skipTest("pytz unavailable")

        self.tst_next_run_time_minute_end("Europe/London")

    def test_next_run_time_minute_end_katmhandu(self):
        try:
            import pytz
        except ModuleNotFoundError:
            self.skipTest("pytz unavailable")

        self.tst_next_run_time_minute_end("Asia/Kathmandu")

    def tst_next_run_time_minute_end(self, tz):
        mock_job = make_mock_job()
        with mock_datetime(2010, 10, 10, 10, 10, 0):
            job = every().minute.at(":15", tz).do(mock_job)
            assert job.next_run.minute == 10
            assert job.next_run.second == 15

        with mock_datetime(2010, 10, 10, 10, 10, 59):
            job.run()
            assert job.next_run.minute == 11
            assert job.next_run.second == 15

        with mock_datetime(2010, 10, 10, 10, 12, 14):
            job.run()
            assert job.next_run.minute == 12
            assert job.next_run.second == 15

        with mock_datetime(2010, 10, 10, 10, 12, 16):
            job.run()
            assert job.next_run.minute == 13
            assert job.next_run.second == 15

    def test_tz(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2022, 2, 1, 23, 15):
            # Current Berlin time: feb-1 23:15 (local)
            # Current India time: feb-2 03:45
            # Expected to run India time: feb-2 06:30
            # Next run Berlin time: feb-2 02:00
            next = every().day.at("06:30", "Asia/Kolkata").do(mock_job).next_run
            assert next.day == 2
            assert next.hour == 2
            assert next.minute == 0

    def test_tz_daily_midnight(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 4, 14, 4, 50):
            # Current Berlin time: april-14 04:50 (local) (during daylight saving)
            # Current US/Central time: april-13 21:50
            # Expected to run US/Central time: april-14 00:00
            # Next run Berlin time: april-14 07:00
            next = every().day.at("00:00", "US/Central").do(mock_job).next_run
            assert next.day == 14
            assert next.hour == 7
            assert next.minute == 0

    def test_tz_daily_half_hour_offset(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2022, 4, 8, 10, 0):
            # Current Berlin time: 10:00 (local) (during daylight saving)
            # Current NY time: 04:00
            # Expected to run NY time: 10:30
            # Next run Berlin time: 16:30
            next = every().day.at("10:30", "America/New_York").do(mock_job).next_run
            assert next.hour == 16
            assert next.minute == 30

    def test_tz_daily_dst(self):
        mock_job = self.make_tz_mock_job()
        import pytz

        with mock_datetime(2022, 3, 20, 10, 0):
            # Current Berlin time: 10:00 (local) (NOT during daylight saving)
            # Current NY time: 04:00 (during daylight saving)
            # Expected to run NY time: 10:30
            # Next run Berlin time: 15:30
            tz = pytz.timezone("America/New_York")
            next = every().day.at("10:30", tz).do(mock_job).next_run
            assert next.hour == 15
            assert next.minute == 30

    def test_tz_daily_dst_skip_hour(self):
        mock_job = self.make_tz_mock_job()
        # Test the DST-case that is described in the documentation
        with mock_datetime(2023, 3, 26, 1, 30):
            # Current Berlin time: 01:30 (NOT during daylight saving)
            # Expected to run: 02:30 - this time doesn't exist
            #  because clock moves from 02:00 to 03:00
            # Next run: 03:30
            job = every().day.at("02:30", "Europe/Berlin").do(mock_job)
            assert job.next_run.day == 26
            assert job.next_run.hour == 3
            assert job.next_run.minute == 30
        with mock_datetime(2023, 3, 27, 1, 30):
            # the next day the job shall again run at 02:30
            job.run()
            assert job.next_run.day == 27
            assert job.next_run.hour == 2
            assert job.next_run.minute == 30

    def test_tz_daily_dst_overlap_hour(self):
        mock_job = self.make_tz_mock_job()
        # Test the DST-case that is described in the documentation
        with mock_datetime(2023, 10, 29, 1, 30):
            # Current Berlin time: 01:30 (during daylight saving)
            # Expected to run: 02:30 - this time exists twice
            #  because clock moves from 03:00 to 02:00
            # Next run should be at the first occurrence of 02:30
            job = every().day.at("02:30", "Europe/Berlin").do(mock_job)
            assert job.next_run.day == 29
            assert job.next_run.hour == 2
            assert job.next_run.minute == 30
        with mock_datetime(2023, 10, 29, 2, 35):
            # After the job runs, the next run should be scheduled on the next day at 02:30
            job.run()
            assert job.next_run.day == 30
            assert job.next_run.hour == 2
            assert job.next_run.minute == 30

    def test_tz_daily_exact_future_scheduling(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2022, 3, 20, 10, 0):
            # Current Berlin time: 10:00 (local) (NOT during daylight saving)
            # Current Krasnoyarsk time: 16:00
            # Expected to run Krasnoyarsk time: mar-21 11:00
            # Next run Berlin time: mar-21 05:00
            # Expected idle seconds: 68400
            schedule.clear()
            every().day.at("11:00", "Asia/Krasnoyarsk").do(mock_job)
            expected_delta = (
                datetime.datetime(2022, 3, 21, 5, 0) - datetime.datetime.now()
            )
            assert schedule.idle_seconds() == expected_delta.total_seconds()

    def test_tz_daily_utc(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 9, 18, 10, 59, 0, TZ_AUCKLAND):
            # Testing issue #598
            # Current Auckland time: 10:59 (local) (NOT during daylight saving)
            # Current UTC time: 21:59 (17 september)
            # Expected to run UTC time: sept-18 00:00
            # Next run Auckland time: sept-18 12:00
            schedule.clear()
            next = every().day.at("00:00", "UTC").do(mock_job).next_run
            assert next.day == 18
            assert next.hour == 12
            assert next.minute == 0

            # Test that .day.at() and .monday.at() are equivalent in this case
            schedule.clear()
            next = every().monday.at("00:00", "UTC").do(mock_job).next_run
            assert next.day == 18
            assert next.hour == 12
            assert next.minute == 0

    def test_tz_daily_issue_592(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 7, 15, 13, 0, 0, TZ_UTC):
            # Testing issue #592
            # Current UTC time: 13:00
            # Expected to run US East time: 9:45 (daylight saving active)
            # Next run UTC time: july-15 13:45
            schedule.clear()
            next = every().day.at("09:45", "US/Eastern").do(mock_job).next_run
            assert next.day == 15
            assert next.hour == 13
            assert next.minute == 45

    def test_tz_daily_exact_seconds_precision(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 10, 19, 15, 0, 0, TZ_UTC):
            # Testing issue #603
            # Current UTC: oktober-19 15:00
            # Current Amsterdam: oktober-19 17:00 (daylight saving active)
            # Expected run Amsterdam: oktober-20 00:00:20 (daylight saving active)
            # Next run UTC time: oktober-19 22:00:20
            schedule.clear()
            next = every().day.at("00:00:20", "Europe/Amsterdam").do(mock_job).next_run
            assert next.day == 19
            assert next.hour == 22
            assert next.minute == 00
            assert next.second == 20

    def test_tz_weekly_sunday_conversion(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 10, 22, 23, 0, 0, TZ_UTC):
            # Current UTC: sunday 22-okt 23:00
            # Current Amsterdam: monday 23-okt 01:00 (daylight saving active)
            # Expected run Amsterdam: sunday 29 oktober 23:00 (daylight saving NOT active)
            # Next run UTC time: oktober-29 22:00
            schedule.clear()
            next = every().sunday.at("23:00", "Europe/Amsterdam").do(mock_job).next_run
            assert next.day == 29
            assert next.hour == 22
            assert next.minute == 00

    def test_tz_daily_new_year_offset(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 12, 31, 23, 0, 0):
            # Current Berlin time: dec-31 23:00 (local)
            # Current Sydney time: jan-1 09:00 (next day)
            # Expected to run Sydney time: jan-1 12:00
            # Next run Berlin time: jan-1 02:00
            next = every().day.at("12:00", "Australia/Sydney").do(mock_job).next_run
            assert next.day == 1
            assert next.hour == 2
            assert next.minute == 0

    def test_tz_daily_end_year_cross_continent(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 12, 31, 23, 50):
            # End of the year in Berlin
            # Current Berlin time: dec-31 23:50
            # Current Tokyo time: jan-1 07:50 (next day)
            # Expected to run Tokyo time: jan-1 09:00
            # Next run Berlin time: jan-1 01:00
            next = every().day.at("09:00", "Asia/Tokyo").do(mock_job).next_run
            assert next.day == 1
            assert next.hour == 1
            assert next.minute == 0

    def test_tz_daily_end_month_offset(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 2, 28, 23, 50):
            # End of the month (non-leap year) in Berlin
            # Current Berlin time: feb-28 23:50
            # Current Sydney time: mar-1 09:50 (next day)
            # Expected to run Sydney time: mar-1 10:00
            # Next run Berlin time: mar-1 00:00
            next = every().day.at("10:00", "Australia/Sydney").do(mock_job).next_run
            assert next.day == 1
            assert next.hour == 0
            assert next.minute == 0

    def test_tz_daily_leap_year(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2024, 2, 28, 23, 50):
            # End of the month (leap year) in Berlin
            # Current Berlin time: feb-28 23:50
            # Current Dubai time: feb-29 02:50
            # Expected to run Dubai time: feb-29 04:00
            # Next run Berlin time: feb-29 01:00
            next = every().day.at("04:00", "Asia/Dubai").do(mock_job).next_run
            assert next.month == 2
            assert next.day == 29
            assert next.hour == 1
            assert next.minute == 0

    def test_tz_daily_issue_605(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 9, 18, 10, 00, 0, TZ_AUCKLAND):
            schedule.clear()
            # Testing issue #605
            # Current time: Monday 18 September 10:00 NZST
            # Current time UTC: Sunday 17 September 22:00
            # We expect the job to run at 23:00 on Sunday 17 September NZST
            # That is an expected idle time of 1 hour
            # Expected next run in NZST: 2023-09-18 11:00:00
            next = schedule.every().day.at("23:00", "UTC").do(mock_job).next_run
            assert round(schedule.idle_seconds() / 3600) == 1
            assert next.day == 18
            assert next.hour == 11
            assert next.minute == 0

    def test_tz_daily_dst_starting_point(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 3, 26, 1, 30):
            # Daylight Saving Time starts in Berlin
            # In Berlin, 26 March 2023, 02:00:00 clocks were turned forward 1 hour
            # In London, 26 March 2023, 01:00:00 clocks were turned forward 1 hour
            # Current Berlin time:  26 March 01:30 (UTC+1)
            # Current London time:  26 March 00:30 (UTC+0)
            # Expected London time: 26 March 02:00 (UTC+1)
            # Expected Berlin time: 26 March 03:00 (UTC+2)
            next = every().day.at("01:00", "Europe/London").do(mock_job).next_run
            assert next.day == 26
            assert next.hour == 3
            assert next.minute == 0

    def test_tz_daily_dst_ending_point(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 10, 29, 2, 30, fold=1):
            # Daylight Saving Time ends in Berlin
            # Current Berlin time: oct-29 02:30 (after moving back to 02:00 due to DST end)
            # Current Istanbul time: oct-29 04:30
            # Expected to run Istanbul time: oct-29 06:00
            # Next run Berlin time: oct-29 04:00
            next = every().day.at("06:00", "Europe/Istanbul").do(mock_job).next_run
            assert next.hour == 4
            assert next.minute == 0

    def test_tz_daily_issue_608_pre_dst(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 9, 18, 10, 00, 0, TZ_AUCKLAND):
            # See ticket #608
            # Testing timezone conversion the week before daylight saving comes into effect
            # Current time: Monday 18 September 10:00 NZST
            # Current time UTC: Sunday 17 September 22:00
            # Expected next run in NZST: 2023-09-18 11:00:00
            schedule.clear()
            next = schedule.every().day.at("23:00", "UTC").do(mock_job).next_run
            assert next.day == 18
            assert next.hour == 11
            assert next.minute == 0

    def test_tz_daily_issue_608_post_dst(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2024, 4, 8, 10, 00, 0, TZ_AUCKLAND):
            # See ticket #608
            # Testing timezone conversion the week after daylight saving ends
            # Current time: Monday 8 April 10:00 NZST
            # Current time UTC: Sunday 7 April 22:00
            # Expected next run in NZDT: 2023-04-08 11:00:00
            schedule.clear()
            next = schedule.every().day.at("23:00", "UTC").do(mock_job).next_run
            assert next.day == 8
            assert next.hour == 11
            assert next.minute == 0

    def test_tz_daily_issue_608_mid_dst(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2023, 9, 25, 10, 00, 0, TZ_AUCKLAND):
            # See ticket #608
            # Testing timezone conversion during the week after daylight saving comes into effect
            # Current time: Monday 25 September 10:00 NZDT
            # Current time UTC: Sunday 24 September 21:00
            # Expected next run in UTC:  2023-09-24 23:00
            # Expected next run in NZDT: 2023-09-25 12:00
            schedule.clear()
            next = schedule.every().day.at("23:00", "UTC").do(mock_job).next_run
            assert next.month == 9
            assert next.day == 25
            assert next.hour == 12
            assert next.minute == 0

    def test_tz_daily_issue_608_before_dst_end(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2024, 4, 1, 10, 00, 0, TZ_AUCKLAND):
            # See ticket #608
            # Testing timezone conversion during the week before daylight saving ends
            # Current time: Monday 1 April 10:00 NZDT
            # Current time UTC: Friday 31 March 21:00
            # Expected next run in UTC:  2023-03-31 23:00
            # Expected next run in NZDT: 2024-04-01 12:00
            schedule.clear()
            next = schedule.every().day.at("23:00", "UTC").do(mock_job).next_run
            assert next.month == 4
            assert next.day == 1
            assert next.hour == 12
            assert next.minute == 0

    def test_tz_hourly_intermediate_conversion(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2024, 5, 4, 14, 37, 22, TZ_CHATHAM):
            # Crurent time: 14:37:22  New Zealand, Chatham Islands (UTC +12:45)
            # Current time: 3 may, 23:22:22 Canada, Newfoundland (UTC -2:30)
            # Exected next run in Newfoundland: 4 may, 09:14:45
            # Expected next run in Chatham: 5 may, 00:29:45
            schedule.clear()
            next = (
                schedule.every(10)
                .hours.at("14:45", "Canada/Newfoundland")
                .do(mock_job)
                .next_run
            )
            assert next.day == 5
            assert next.hour == 0
            assert next.minute == 29
            assert next.second == 45

    def test_tz_minutes_year_round(self):
        mock_job = self.make_tz_mock_job()
        # Test a full year of scheduling across timezones, where one timezone
        # is in the northern hemisphere and the other in the southern hemisphere
        # These two timezones are also a bit exotic (not the usual UTC+1, UTC-1)
        # Local timezone: Newfoundland, Canada: UTC-2:30 / DST UTC-3:30
        # Remote timezone: Chatham Islands, New Zealand: UTC+12:45 / DST UTC+13:45
        schedule.clear()
        job = schedule.every(20).minutes.at(":13", "Canada/Newfoundland").do(mock_job)
        with mock_datetime(2024, 9, 29, 2, 20, 0, TZ_CHATHAM):
            # First run, nothing special, no utc-offset change
            # Current time: 29 sept, 02:20:00  Chatham
            # Current time: 28 sept, 11:05:00  Newfoundland
            # Expected time: 28 sept, 11:20:13 Newfoundland
            # Expected time: 29 sept, 02:40:13 Chatham
            job.run()
            assert job.next_run.day == 29
            assert job.next_run.hour == 2
            assert job.next_run.minute == 40
            assert job.next_run.second == 13
        with mock_datetime(2024, 9, 29, 2, 40, 14, TZ_CHATHAM):
            # next-schedule happens 1 second behind schedule
            job.run()
            # On 29 Sep, 02:45 2024, in Chatham, the clock is moved +1 hour
            # Thus, the next run happens AFTER the local timezone exits DST
            # Current time:  29 sept, 02:40:14 Chatham      (UTC +12:45)
            # Current time:  28 sept, 11:25:14 Newfoundland (UTC -2:30)
            # Expected time: 28 sept, 11:45:13 Newfoundland (UTC -2:30)
            # Expected time: 29 sept, 04:00:13 Chatham      (UTC +13:45)
            assert job.next_run.day == 29
            assert job.next_run.hour == 4
            assert job.next_run.minute == 00
            assert job.next_run.second == 13
        with mock_datetime(2024, 11, 3, 2, 23, 55, TZ_CHATHAM, fold=0):
            # Time is right before Newfoundland exits DST
            # Local time will move 1 hour back at 03:00

            job.run()
            # There are no timezone switches yet, nothing special going on:
            # Current time:  3 Nov, 02:23:55 Chatham
            # Expected time: 3 Nov, 02:43:13 Chatham
            assert job.next_run.day == 3
            assert job.next_run.hour == 2
            assert job.next_run.minute == 43  # Within the fold, first occurrence
            assert job.next_run.second == 13
        with mock_datetime(2024, 11, 3, 2, 23, 55, TZ_CHATHAM, fold=1):
            # Time is during the fold. Local time has moved back 1 hour, this is
            # the second occurrence of the 02:23 time.

            job.run()
            # Current time:  3 Nov, 02:23:55 Chatham
            # Expected time: 3 Nov, 02:43:13 Chatham
            assert job.next_run.day == 3
            assert job.next_run.hour == 2
            assert job.next_run.minute == 43
            assert job.next_run.second == 13
        with mock_datetime(2025, 3, 9, 19, 00, 00, TZ_CHATHAM):
            # Time is right before Newfoundland enters DST
            # At 02:00, the remote clock will move forward 1 hour

            job.run()
            # Current time:  9 March, 19:00:00 Chatham      (UTC +13:45)
            # Current time:  9 March, 01:45:00 Newfoundland (UTC -3:30)
            # Expected time: 9 March, 03:05:13 Newfoundland (UTC -2:30)
            # Expected time  9 March, 19:20:13 Chatham      (UTC +13:45)

            assert job.next_run.day == 9
            assert job.next_run.hour == 19
            assert job.next_run.minute == 20
            assert job.next_run.second == 13
        with mock_datetime(2025, 4, 7, 17, 55, 00, TZ_CHATHAM):
            # Time is within the few hours before Catham exits DST
            # At 03:45, the local clock moves back 1 hour

            job.run()
            # Current time:  7 April, 17:55:00 Chatham
            # Current time:  7 April, 02:40:00 Newfoundland
            # Expected time: 7 April, 03:00:13 Newfoundland
            # Expected time  7 April, 18:15:13 Chatham
            assert job.next_run.day == 7
            assert job.next_run.hour == 18
            assert job.next_run.minute == 15
            assert job.next_run.second == 13
        with mock_datetime(2025, 4, 7, 18, 55, 00, TZ_CHATHAM):
            # Schedule the next run exactly when the clock moved backwards
            # Curren time is before the clock-move, next run is after the clock change

            job.run()
            # Current time:  7 April, 18:55:00 Chatham
            # Current time:  7 April, 03:40:00 Newfoundland
            # Expected time: 7 April, 03:00:13 Newfoundland (clock moved back)
            # Expected time  7 April, 19:15:13 Chatham
            assert job.next_run.day == 7
            assert job.next_run.hour == 19
            assert job.next_run.minute == 15
            assert job.next_run.second == 13
        with mock_datetime(2025, 4, 7, 19, 15, 13, TZ_CHATHAM):
            # Schedule during the fold in the remote timezone

            job.run()
            # Current time:  7 April, 19:15:13 Chatham
            # Current time:  7 April, 03:00:13 Newfoundland (fold)
            # Expected time: 7 April, 03:20:13 Newfoundland (fold)
            # Expected time: 7 April, 19:35:13 Chatham
            assert job.next_run.day == 7
            assert job.next_run.hour == 19
            assert job.next_run.minute == 35
            assert job.next_run.second == 13

    def test_tz_weekly_large_interval_forward(self):
        mock_job = self.make_tz_mock_job()
        # Testing scheduling large intervals that skip over clock move forward
        with mock_datetime(2024, 3, 28, 11, 0, 0, TZ_BERLIN):
            # At March 31st 2024, 02:00:00 clocks were turned forward 1 hour
            schedule.clear()
            next = (
                schedule.every(7)
                .days.at("11:00", "Europe/Berlin")
                .do(mock_job)
                .next_run
            )
            assert next.month == 4
            assert next.day == 4
            assert next.hour == 11
            assert next.minute == 0
            assert next.second == 0

    def test_tz_weekly_large_interval_backward(self):
        mock_job = self.make_tz_mock_job()
        import pytz

        # Testing scheduling large intervals that skip over clock move back
        with mock_datetime(2024, 10, 25, 11, 0, 0, TZ_BERLIN):
            # At March 31st 2024, 02:00:00 clocks were turned forward 1 hour
            schedule.clear()
            next = (
                schedule.every(7)
                .days.at("11:00", "Europe/Berlin")
                .do(mock_job)
                .next_run
            )
            assert next.month == 11
            assert next.day == 1
            assert next.hour == 11
            assert next.minute == 0
            assert next.second == 0

    def test_tz_daily_skip_dst_change(self):
        mock_job = self.make_tz_mock_job()
        with mock_datetime(2024, 11, 3, 10, 0):
            # At 3 November 2024, 02:00:00 clocks are turned backward 1 hour
            # The job skips the whole DST change becaus it runs at 14:00
            # Current time Berlin:     3 Nov, 10:00
            # Current time Anchorage:  3 Nov, 00:00 (UTC-08:00)
            # Expected time Anchorage: 3 Nov, 14:00 (UTC-09:00)
            # Expected time Berlin:    4 Nov, 00:00
            schedule.clear()
            next = (
                schedule.every()
                .day.at("14:00", "America/Anchorage")
                .do(mock_job)
                .next_run
            )
            assert next.day == 4
            assert next.hour == 0
            assert next.minute == 00

    def test_tz_daily_different_simultaneous_dst_change(self):
        mock_job = self.make_tz_mock_job()

        # TZ_BERLIN_EXTRA is the same as Berlin, but during summer time
        # moves the clock 2 hours forward instead of 1
        # This is a fictional timezone
        TZ_BERLIN_EXTRA = "CET-01CEST-03,M3.5.0,M10.5.0/3"
        with mock_datetime(2024, 3, 31, 0, 0, 0, TZ_BERLIN_EXTRA):
            # In Berlin at March 31 2024, 02:00:00 clocks were turned forward 1 hour
            # In Berlin Extra, the clocks move forward 2 hour at the same time
            # Current time Berlin Extra:  31 Mar, 00:00 (UTC+01:00)
            # Current time Berlin:        31 Mar, 00:00 (UTC+01:00)
            # Expected time Berlin:       31 Mar, 10:00 (UTC+02:00)
            # Expected time Berlin Extra: 31 Mar, 11:00 (UTC+03:00)
            schedule.clear()
            next = (
                schedule.every().day.at("10:00", "Europe/Berlin").do(mock_job).next_run
            )
            assert next.day == 31
            assert next.hour == 11
            assert next.minute == 00

    def test_tz_daily_opposite_dst_change(self):
        mock_job = self.make_tz_mock_job()

        # TZ_BERLIN_INVERTED changes in the opposite direction of Berlin
        # This is a fictional timezone
        TZ_BERLIN_INVERTED = "CET-1CEST,M10.5.0/3,M3.5.0"
        with mock_datetime(2024, 3, 31, 0, 0, 0, TZ_BERLIN_INVERTED):
            # In Berlin at March 31 2024, 02:00:00 clocks were turned forward 1 hour
            # In Berlin Inverted, the clocks move back 1 hour at the same time
            # Current time Berlin Inverted:  31 Mar, 00:00 (UTC+02:00)
            # Current time Berlin:           31 Mar, 00:00 (UTC+01:00)
            # Expected time Berlin:          31 Mar, 10:00 (UTC+02:00) +9 hour
            # Expected time Berlin Inverted: 31 Mar, 09:00 (UTC+01:00)
            schedule.clear()
            next = (
                schedule.every().day.at("10:00", "Europe/Berlin").do(mock_job).next_run
            )
            assert next.day == 31
            assert next.hour == 9
            assert next.minute == 00

    def test_tz_invalid_timezone_exceptions(self):
        mock_job = self.make_tz_mock_job()
        import pytz

        with self.assertRaises(pytz.exceptions.UnknownTimeZoneError):
            every().day.at("10:30", "FakeZone").do(mock_job)

        with self.assertRaises(ScheduleValueError):
            every().day.at("10:30", 43).do(mock_job)

    def test_align_utc_offset_no_timezone(self):
        job = schedule.every().day.at("10:00").do(make_mock_job())
        now = datetime.datetime(2024, 5, 11, 10, 30, 55, 0)
        aligned_time = job._correct_utc_offset(now, fixate_time=True)
        self.assertEqual(now, aligned_time)

    def setup_utc_offset_test(self):
        try:
            import pytz
        except ModuleNotFoundError:
            self.skipTest("pytz unavailable")
        job = (
            schedule.every()
            .day.at("10:00", "Europe/Berlin")
            .do(make_mock_job("tz-test"))
        )
        tz = pytz.timezone("Europe/Berlin")
        return (job, tz)

    def test_align_utc_offset_no_change(self):
        (job, tz) = self.setup_utc_offset_test()
        now = tz.localize(datetime.datetime(2023, 3, 26, 1, 30))
        aligned_time = job._correct_utc_offset(now, fixate_time=False)
        self.assertEqual(now, aligned_time)

    def test_align_utc_offset_with_dst_gap(self):
        (job, tz) = self.setup_utc_offset_test()
        # Non-existent time in Berlin timezone
        gap_time = tz.localize(datetime.datetime(2024, 3, 31, 2, 30, 0))
        aligned_time = job._correct_utc_offset(gap_time, fixate_time=True)

        assert aligned_time.utcoffset() == datetime.timedelta(hours=2)
        assert aligned_time.day == 31
        assert aligned_time.hour == 3
        assert aligned_time.minute == 30

    def test_align_utc_offset_with_dst_fold(self):
        (job, tz) = self.setup_utc_offset_test()
        # This time exists twice, this is the first occurance
        overlap_time = tz.localize(datetime.datetime(2024, 10, 27, 2, 30))
        aligned_time = job._correct_utc_offset(overlap_time, fixate_time=False)
        # Since the time exists twice, no fixate_time flag should yield the first occurrence
        first_occurrence = tz.localize(datetime.datetime(2024, 10, 27, 2, 30, fold=0))
        self.assertEqual(first_occurrence, aligned_time)

    def test_align_utc_offset_with_dst_fold_fixate_1(self):
        (job, tz) = self.setup_utc_offset_test()
        # This time exists twice, this is the 1st occurance
        overlap_time = tz.localize(datetime.datetime(2024, 10, 27, 1, 30), is_dst=True)
        overlap_time += datetime.timedelta(
            hours=1
        )  # puts it at 02:30+02:00 (Which exists once)

        aligned_time = job._correct_utc_offset(overlap_time, fixate_time=True)
        # The time should not have moved, because the original time is valid
        assert aligned_time.utcoffset() == datetime.timedelta(hours=2)
        assert aligned_time.hour == 2
        assert aligned_time.minute == 30
        assert aligned_time.day == 27

    def test_align_utc_offset_with_dst_fold_fixate_2(self):
        (job, tz) = self.setup_utc_offset_test()
        # 02:30 exists twice, this is the 2nd occurance
        overlap_time = tz.localize(datetime.datetime(2024, 10, 27, 2, 30), is_dst=False)
        # The time 2024-10-27 02:30:00+01:00 exists once

        aligned_time = job._correct_utc_offset(overlap_time, fixate_time=True)
        # The time was valid, should not have been moved
        assert aligned_time.utcoffset() == datetime.timedelta(hours=1)
        assert aligned_time.hour == 2
        assert aligned_time.minute == 30
        assert aligned_time.day == 27

    def test_align_utc_offset_after_fold_fixate(self):
        (job, tz) = self.setup_utc_offset_test()
        # This time is 30 minutes after a folded hour.
        duplicate_time = tz.localize(datetime.datetime(2024, 10, 27, 2, 30))
        duplicate_time += datetime.timedelta(hours=1)

        aligned_time = job._correct_utc_offset(duplicate_time, fixate_time=False)

        assert aligned_time.utcoffset() == datetime.timedelta(hours=1)
        assert aligned_time.hour == 3
        assert aligned_time.minute == 30
        assert aligned_time.day == 27

    def test_daylight_saving_time(self):
        mock_job = make_mock_job()
        # 27 March 2022, 02:00:00 clocks were turned forward 1 hour
        with mock_datetime(2022, 3, 27, 0, 0):
            assert every(4).hours.do(mock_job).next_run.hour == 4

        # Sunday, 30 October 2022, 03:00:00 clocks were turned backward 1 hour
        with mock_datetime(2022, 10, 30, 0, 0):
            assert every(4).hours.do(mock_job).next_run.hour == 4

    def test_move_to_next_weekday_today(self):
        monday = datetime.datetime(2024, 5, 13, 10, 27, 54)
        tuesday = schedule._move_to_next_weekday(monday, "monday")
        assert tuesday.day == 13  # today! Time didn't change.
        assert tuesday.hour == 10
        assert tuesday.minute == 27

    def test_move_to_next_weekday_tommorrow(self):
        monday = datetime.datetime(2024, 5, 13, 10, 27, 54)
        tuesday = schedule._move_to_next_weekday(monday, "tuesday")
        assert tuesday.day == 14  # 1 day ahead
        assert tuesday.hour == 10
        assert tuesday.minute == 27

    def test_move_to_next_weekday_nextweek(self):
        wednesday = datetime.datetime(2024, 5, 15, 10, 27, 54)
        tuesday = schedule._move_to_next_weekday(wednesday, "tuesday")
        assert tuesday.day == 21  # next week monday
        assert tuesday.hour == 10
        assert tuesday.minute == 27

    def test_run_all(self):
        mock_job = make_mock_job()
        every().minute.do(mock_job)
        every().hour.do(mock_job)
        every().day.at("11:00").do(mock_job)
        schedule.run_all()
        assert mock_job.call_count == 3

    def test_run_all_with_decorator(self):
        mock_job = make_mock_job()

        @repeat(every().minute)
        def job1():
            mock_job()

        @repeat(every().hour)
        def job2():
            mock_job()

        @repeat(every().day.at("11:00"))
        def job3():
            mock_job()

        schedule.run_all()
        assert mock_job.call_count == 3

    def test_run_all_with_decorator_args(self):
        mock_job = make_mock_job()

        @repeat(every().minute, 1, 2, "three", foo=23, bar={})
        def job(*args, **kwargs):
            mock_job(*args, **kwargs)

        schedule.run_all()
        mock_job.assert_called_once_with(1, 2, "three", foo=23, bar={})

    def test_run_all_with_decorator_defaultargs(self):
        mock_job = make_mock_job()

        @repeat(every().minute)
        def job(nothing=None):
            mock_job(nothing)

        schedule.run_all()
        mock_job.assert_called_once_with(None)

    def test_job_func_args_are_passed_on(self):
        mock_job = make_mock_job()
        every().second.do(mock_job, 1, 2, "three", foo=23, bar={})
        schedule.run_all()
        mock_job.assert_called_once_with(1, 2, "three", foo=23, bar={})

    def test_to_string(self):
        def job_fun():
            pass

        s = str(every().minute.do(job_fun, "foo", bar=23))
        assert s == (
            "Job(interval=1, unit=minutes, do=job_fun, "
            "args=('foo',), kwargs={'bar': 23})"
        )
        assert "job_fun" in s
        assert "foo" in s
        assert "{'bar': 23}" in s

    def test_to_repr(self):
        def job_fun():
            pass

        s = repr(every().minute.do(job_fun, "foo", bar=23))
        assert s.startswith(
            "Every 1 minute do job_fun('foo', bar=23) (last run: [never], next run: "
        )
        assert "job_fun" in s
        assert "foo" in s
        assert "bar=23" in s

        # test repr when at_time is not None
        s2 = repr(every().day.at("00:00").do(job_fun, "foo", bar=23))
        assert s2.startswith(
            (
                "Every 1 day at 00:00:00 do job_fun('foo', "
                "bar=23) (last run: [never], next run: "
            )
        )

        # Ensure Job.__repr__ does not throw exception on a partially-composed Job
        s3 = repr(schedule.every(10))
        assert s3 == "Every 10 None do [None] (last run: [never], next run: [never])"

    def test_to_string_lambda_job_func(self):
        assert len(str(every().minute.do(lambda: 1))) > 1
        assert len(str(every().day.at("10:30").do(lambda: 1))) > 1

    def test_repr_functools_partial_job_func(self):
        def job_fun(arg):
            pass

        job_fun = functools.partial(job_fun, "foo")
        job_repr = repr(every().minute.do(job_fun, bar=True, somekey=23))
        assert "functools.partial" in job_repr
        assert "bar=True" in job_repr
        assert "somekey=23" in job_repr

    def test_to_string_functools_partial_job_func(self):
        def job_fun(arg):
            pass

        job_fun = functools.partial(job_fun, "foo")
        job_str = str(every().minute.do(job_fun, bar=True, somekey=23))
        assert "functools.partial" in job_str
        assert "bar=True" in job_str
        assert "somekey=23" in job_str

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
        with mock_datetime(2010, 1, 6, 13, 16):  # january 6 2010 == Wednesday
            every().wednesday.at("14:12").do(mock_job)
            schedule.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 6, 14, 16):
            schedule.run_pending()
            assert mock_job.call_count == 1

    def test_run_every_weekday_at_specific_time_past_today(self):
        mock_job = make_mock_job()
        with mock_datetime(2010, 1, 6, 13, 16):
            every().wednesday.at("13:15").do(mock_job)
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
            every(2).days.at("11:30").do(mock_job)
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
            hourly_job = make_mock_job("hourly")
            daily_job = make_mock_job("daily")
            every().day.do(daily_job)
            every().hour.do(hourly_job)
            assert len(schedule.jobs) == 2
            # Make sure the hourly job is first
            assert schedule.next_run() == original_datetime(2010, 1, 6, 14, 16)

    def test_idle_seconds(self):
        assert schedule.default_scheduler.next_run is None
        assert schedule.idle_seconds() is None

        mock_job = make_mock_job()
        with mock_datetime(2020, 12, 9, 21, 46):
            job = every().hour.do(mock_job)
            assert schedule.idle_seconds() == 60 * 60
            schedule.cancel_job(job)
            assert schedule.next_run() is None
            assert schedule.idle_seconds() is None

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

        schedule.cancel_job("Not a job")
        assert len(schedule.jobs) == 1
        schedule.default_scheduler.cancel_job("Not a job")
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
        job1 = every().second.do(make_mock_job(name="job1"))
        self.assertRaises(TypeError, job1.tag, {})
        self.assertRaises(TypeError, job1.tag, 1, "a", [])
        job1.tag(0, "a", True)
        assert len(job1.tags) == 3

    def test_get_by_tag(self):
        every().second.do(make_mock_job()).tag("job1", "tag1")
        every().second.do(make_mock_job()).tag("job2", "tag2", "tag4")
        every().second.do(make_mock_job()).tag("job3", "tag3", "tag4")

        # Test None input yields all 3
        jobs = schedule.get_jobs()
        assert len(jobs) == 3
        assert {"job1", "job2", "job3"}.issubset(
            {*jobs[0].tags, *jobs[1].tags, *jobs[2].tags}
        )

        # Test each 1:1 tag:job
        jobs = schedule.get_jobs("tag1")
        assert len(jobs) == 1
        assert "job1" in jobs[0].tags

        # Test multiple jobs found.
        jobs = schedule.get_jobs("tag4")
        assert len(jobs) == 2
        assert "job1" not in {*jobs[0].tags, *jobs[1].tags}

        # Test no tag.
        jobs = schedule.get_jobs("tag5")
        assert len(jobs) == 0
        schedule.clear()
        assert len(schedule.jobs) == 0

    def test_clear_by_tag(self):
        every().second.do(make_mock_job(name="job1")).tag("tag1")
        every().second.do(make_mock_job(name="job2")).tag("tag1", "tag2")
        every().second.do(make_mock_job(name="job3")).tag(
            "tag3", "tag3", "tag3", "tag2"
        )
        assert len(schedule.jobs) == 3
        schedule.run_all()
        assert len(schedule.jobs) == 3
        schedule.clear("tag3")
        assert len(schedule.jobs) == 2
        schedule.clear("tag1")
        assert len(schedule.jobs) == 0
        every().second.do(make_mock_job(name="job1"))
        every().second.do(make_mock_job(name="job2"))
        every().second.do(make_mock_job(name="job3"))
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
