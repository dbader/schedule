Asyncio & Coroutines
====================

This example shows how to schedule an async job on the asyncio event loop.

.. code-block:: python
    import schedule
    import asyncio

    async def job_async():
        print("I am an async job")
        await asyncio.sleep(1)

    schedule.every(5).seconds.do(lambda: asyncio.create_task(job_async()))

    async def scheduler():
        while True:
            await asyncio.sleep(1)
            schedule.run_pending()

    asyncio.run(scheduler())

The call to ``asyncio.create_task()`` submits the ``job_async`` coroutine to the asyncio event loop.
it may or may not run immediately, depending on the how busy the event loop is.

Sleeping the right amount of time
---------------------------------

The ``scheduler()`` can be optimized by sleeping *exactly* [1]_ the amount of time until the next job is scheduled to run:

.. code-block:: python
    async def scheduler():
        seconds = schedule.idle_seconds()
        while seconds is not None:
            if seconds > 0:
                # sleep exactly the right amount of time
                await asyncio.sleep(seconds)
            schedule.run_pending()

asyncio.run(scheduler())
Keep in mind that if a new job is scheduled while sleeping, the new job's earliest run is whenever the sleep finishes.




.. rubric:: Footnotes
.. [1] `asyncio.sleep` may sleep little more then expected, depending on loop implementation of loop and system load