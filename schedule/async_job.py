# module: schedule
# file: async_job.py
import inspect

from schedule.job import Job


def _inherit_doc(doc):
    return doc.replace(
        'Scheduler',
        'AsyncScheduler').replace(
        'job',
        'async job').replace(
        'Job',
        'AsyncJob')


class AsyncJob(Job):
    __doc__ = _inherit_doc(Job.__doc__)

    async def run(self):
        ret = super().run()
        if inspect.isawaitable(ret):
            ret = await ret

        return ret

    run.__doc__ = _inherit_doc(Job.run.__doc__)
