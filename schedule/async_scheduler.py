import asyncio
import logging

from schedule.scheduler import CancelJob, Scheduler

logger = logging.getLogger('async_schedule')


class AsyncScheduler(Scheduler):

    async def run_pending(self):
        runnable_jobs = (job for job in self.jobs if job.should_run)
        await asyncio.gather(*[self._run_job(job) for job in runnable_jobs])

    async def run_all(self, delay_seconds=0):
        logger.info(f'Running *all* {len(self.jobs)} jobs with {delay_seconds}s delay in between')
        for job in self.jobs[:]:
            await self._run_job(job)
            await asyncio.sleep(delay_seconds)

    async def _run_job(self, job):
        ret = await job.run()
        if isinstance(ret, CancelJob) or ret is CancelJob:
            self.cancel_job(job)
