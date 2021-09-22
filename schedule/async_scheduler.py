"""
Python async job scheduling for humans.

An in-process scheduler for periodic jobs that uses the builder pattern
for configuration. Schedule lets you run Python coroutines periodically
at pre-determined intervals using a simple, human-friendly syntax.

Usage:
    >>> import asyncio
    >>> import schedule
    >>> import time

    >>> async def job(message='stuff'):
    >>>     print("I'm working on:", message)

    >>> async_scheduler = schedule.AsyncScheduler()

    >>> async_scheduler.every(10).minutes.do(job)
    >>> async_scheduler.every(5).to(10).days.do(job)
    >>> async_scheduler.every().hour.do(job, message='things')
    >>> async_scheduler.every().day.at("10:30").do(job)

    >>> while True:
    >>>     await schedule.run_pending()
    >>>     await asyncio.sleep(1)
"""
import asyncio
import inspect
import logging

from schedule.scheduler import Scheduler, BaseScheduler

logger = logging.getLogger("async_schedule")


def _inherit_doc(doc):
    return doc.replace("Scheduler", "AsyncScheduler").replace("job", "async job")


class AsyncScheduler(BaseScheduler):
    __doc__ = _inherit_doc(Scheduler.__doc__)

    async def run_pending(self) -> None:
        runnable_jobs = (job for job in self.jobs if job.should_run)
        await asyncio.gather(*[self._run_job(job) for job in runnable_jobs])

    run_pending.__doc__ = _inherit_doc(Scheduler.run_pending.__doc__)

    async def run_all(self, delay_seconds=0) -> None:
        logger.debug(
            "Running *all* %i jobs with %is delay in between",
            len(self.jobs),
            delay_seconds,
        )
        for job in self.jobs[:]:
            await self._run_job(job)
            await asyncio.sleep(delay_seconds)

    run_all.__doc__ = _inherit_doc(Scheduler.run_all.__doc__)

    async def _run_job(self, job) -> None:
        ret = job.run()
        if inspect.isawaitable(ret):
            ret = await ret

        super()._check_returned_value(job, ret)
