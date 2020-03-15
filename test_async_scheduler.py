"""Unit tests for async_scheduler.py"""
import datetime
import sys
import unittest
import mock

if sys.version_info < (3, 5, 0):
    raise unittest.SkipTest("Coroutines declared with the async/await syntax are supported since version 3.5")

import asyncio
import aiounittest

from schedule import AsyncScheduler, CancelJob
from test_schedule import mock_datetime

async_scheduler = AsyncScheduler()


def make_async_mock_job(name='async_job'):
    job = mock.AsyncMock()
    job.__name__ = name
    return job


async def stop_job():
    return CancelJob


class AsyncSchedulerTest(aiounittest.AsyncTestCase):
    def setUp(self):
        async_scheduler.clear()

    @staticmethod
    async def increment(array, index):
        array[index] += 1

    @unittest.skip("slow demo test")
    async def test_async_sample(self):
        duration = 10  # seconds
        test_array = [0] * duration

        for index, value in enumerate(test_array):
            async_scheduler.every(index + 1).seconds.do(AsyncSchedulerTest.increment, test_array, index)

        start = datetime.datetime.now()
        current = start

        while (current - start).total_seconds() < duration:
            await async_scheduler.run_pending()
            await asyncio.sleep(1)
            current = datetime.datetime.now()

        for index, value in enumerate(test_array):
            position = index + 1
            expected = duration / position
            expected = int(expected) if expected != int(expected) else expected - 1

            self.assertEqual(value, expected, msg=f'unexpected value for {position}th')

    async def test_async_run_pending(self):
        mock_job = make_async_mock_job()

        with mock_datetime(2010, 1, 6, 12, 15):
            async_scheduler.every().minute.do(mock_job)
            async_scheduler.every().hour.do(mock_job)
            async_scheduler.every().day.do(mock_job)
            async_scheduler.every().sunday.do(mock_job)
            await async_scheduler.run_pending()
            assert mock_job.call_count == 0

        with mock_datetime(2010, 1, 6, 12, 16):
            await async_scheduler.run_pending()
            assert mock_job.call_count == 1

        with mock_datetime(2010, 1, 6, 13, 16):
            mock_job.reset_mock()
            await async_scheduler.run_pending()
            assert mock_job.call_count == 2

        with mock_datetime(2010, 1, 7, 13, 16):
            mock_job.reset_mock()
            await async_scheduler.run_pending()
            assert mock_job.call_count == 3

        with mock_datetime(2010, 1, 10, 13, 16):
            mock_job.reset_mock()
            await async_scheduler.run_pending()
            assert mock_job.call_count == 4

    async def test_async_run_all(self):
        mock_job = make_async_mock_job()
        async_scheduler.every().minute.do(mock_job)
        async_scheduler.every().hour.do(mock_job)
        async_scheduler.every().day.at('11:00').do(mock_job)
        await async_scheduler.run_all()
        assert mock_job.call_count == 3

    async def test_async_job_func_args_are_passed_on(self):
        mock_job = make_async_mock_job()
        async_scheduler.every().second.do(mock_job, 1, 2, 'three', foo=23, bar={})
        await async_scheduler.run_all()
        mock_job.assert_called_once_with(1, 2, 'three', foo=23, bar={})

    async def test_cancel_async_job(self):
        mock_job = make_async_mock_job()

        async_scheduler.every().second.do(stop_job)
        mj = async_scheduler.every().second.do(mock_job)
        assert len(async_scheduler.jobs) == 2

        await async_scheduler.run_all()
        assert len(async_scheduler.jobs) == 1
        assert async_scheduler.jobs[0] == mj

        async_scheduler.cancel_job('Not a job')
        assert len(async_scheduler.jobs) == 1

        async_scheduler.cancel_job(mj)
        assert len(async_scheduler.jobs) == 0

    async def test_cancel_async_jobs(self):
        async_scheduler.every().second.do(stop_job)
        async_scheduler.every().second.do(stop_job)
        async_scheduler.every().second.do(stop_job)
        assert len(async_scheduler.jobs) == 3

        await async_scheduler.run_all()
        assert len(async_scheduler.jobs) == 0
