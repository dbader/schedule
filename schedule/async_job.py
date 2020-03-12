import inspect

from schedule.job import Job


class AsyncJob(Job):

    async def run(self):
        ret = super().run()
        if inspect.isawaitable(ret):
            ret = await ret

        return ret
