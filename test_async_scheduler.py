"""Unit tests for async_scheduler.py"""
import sys
import unittest

if sys.version_info < (3, 5, 0):
    raise unittest.SkipTest("Coroutines are supported since version 3.5")

import asyncio
import datetime

import aiounittest

from schedule import AsyncScheduler

async_scheduler = AsyncScheduler()


class AsyncSchedulerTest(aiounittest.AsyncTestCase):
    def setUp(self):
        async_scheduler.clear()

    @staticmethod
    async def increment(array, index):
        array[index] += 1

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
