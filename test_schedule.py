"""Unit tests for schedule.py"""
import unittest

# Silence "missing docstring", "method could be a function",
# "class already defined", and "too many public methods" messages:
# pylint: disable-msg=R0201,C0111,E0102,R0904

import schedule
from schedule import every


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        schedule.clear_all_jobs()

    def test_time_units(self):
        self.assertEqual(every().seconds.unit, 'seconds')
        self.assertEqual(every().minutes.unit, 'minutes')
        self.assertEqual(every().hours.unit, 'hours')
        self.assertEqual(every().days.unit, 'days')
        self.assertEqual(every().weeks.unit, 'weeks')

    def test_singular_time_units_match_plural_units(self):
        self.assertEqual(every().second.unit, every().seconds.unit)
        self.assertEqual(every().minute.unit, every().minutes.unit)
        self.assertEqual(every().hour.unit, every().hours.unit)
        self.assertEqual(every().day.unit, every().days.unit)
        self.assertEqual(every().week.unit, every().weeks.unit)

    def test_job_assignment(self):
        def job():
            pass
        self.assertEqual(every().minute.do(job).func, job)

    def test_at_time(self):
        def job():
            pass
        self.assertEqual(every().day.at('10:30').do(job).next_run.hour, 10)
        self.assertEqual(every().day.at('10:30').do(job).next_run.minute, 30)

    def test_next_run_time(self):
        # Mock datetime.datetime to get predictable (=testable) results.
        import datetime

        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 12, 15)
        original_datetime = datetime.datetime
        datetime.datetime = MockDate

        def job():
            pass
        self.assertEqual(every().minute.do(job).next_run.minute, 16)
        self.assertEqual(every(5).minutes.do(job).next_run.minute, 20)
        self.assertEqual(every().hour.do(job).next_run.hour, 13)
        self.assertEqual(every().day.do(job).next_run.day, 7)
        self.assertEqual(every().week.do(job).next_run.day, 13)

        datetime.datetime = original_datetime

    def test_run_all(self):
        self.num_runs = 0

        def job():
            self.num_runs += 1

        every().minute.do(job)
        every().hour.do(job)
        every().day.at('11:00').do(job)

        schedule.run_all_jobs(delay=0)
        self.assertEquals(self.num_runs, 3)

    def test_to_string(self):
        def job():
            pass
        assert len(str(every().minute.do(job))) > 1

    def test_tick(self):
        """Check that tick() runs pending jobs.
        We do this by overriding datetime.datetime with mock objects
        that represent increasing system times.

        Please note that it is *intended behavior that tick() does not
        run missed jobs*. For example, if you've registered a job that
        should run every minute and you only call tick() in one hour
        increments then your job won't be run 60 times in between but
        only once.
        """
        # Mock datetime.datetime to get predictable (=testable) results.
        import datetime

        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 12, 15)
        original_datetime = datetime.datetime
        datetime.datetime = MockDate

        self.num_runs = 0

        def job():
            self.num_runs += 1

        every().minute.do(job)
        every().hour.do(job)
        every().day.do(job)

        schedule.tick()
        self.assertEquals(self.num_runs, 0)

        # Minutely
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 12, 16)
        datetime.datetime = MockDate
        schedule.tick()
        self.assertEquals(self.num_runs, 1)

        # Minutely, hourly
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 6, 13, 16)
        datetime.datetime = MockDate
        self.num_runs = 0
        schedule.tick()
        self.assertEquals(self.num_runs, 2)

        # Minutely, hourly, daily
        class MockDate(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2010, 1, 6)

            @classmethod
            def now(cls):
                return cls(2010, 1, 7, 13, 16)
        datetime.datetime = MockDate
        self.num_runs = 0
        schedule.tick()
        self.assertEquals(self.num_runs, 3)

        datetime.datetime = original_datetime
