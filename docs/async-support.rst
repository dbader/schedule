Nonblocking scheduling with coroutines
======================================
Fist is good to explain what we mean by nonblocking scheduling.
Most of time during scheduling will be spent in spinning on time.sleep


What it allows
------------------
This allows better handling signals during long sleeps (day long sleeps are relatively fine)
and exiting scheduling loop right away after signal reliably without need of multiple threads.
This may lead to better usage of cpu (due just in time wakeup for next task).
It can also allow running scheduler in asyncio application without blocking it and can force scheduling loop to run.
It also allows nonblocking execution of coroutines.

How?
----
This code will only run on Wednesday regular task and Sunday coroutine task.
Nothing is running in between but code not hangs on system signals and exits loop (on one thread that is impossible without coroutines).

.. code-block:: python
    import schedule
    import asyncio

    print(schedule.every().wednesday.do(lambda: print("It is Wednesday...")))


    def wrap_coroutine(c):
        asyncio.create_task(c())  # coroutine must always be wrapped in create task


    async def something_useful():
        await asyncio.sleep(1)  # some useful async function
        print("is is sunday")


    print(schedule.every().sunday.do(lambda: wrap_coroutine(something_useful)))

    terminateEvent = None
    def setup(): #needs to run on asyncio loop
        import signal
        import platform

        global terminateEvent
        terminateEvent = asyncio.Event() #needs to run on asyncio loop

        def terminate(signum):
            print(f"sayonara, I received {signum}")
            terminateEvent.set()  # kill loop

        isLinux = platform.system() == "Linux" or platform.system() == "Darwin"  # only unix has add_signal_handler

        if isLinux:
            loop = asyncio.get_running_loop() #needs to run on asyncio loop

            def linux_handler(signum):
                def handler():
                    terminate(signum)

                loop.add_signal_handler(signum, handler)

            handleSignal = linux_handler
        else: 
            def windows_handler(signum):
                def wrapper(sig, frame):
                    terminate(sig)

                signal.signal(signum, wrapper)

            handleSignal = windows_handler

        handleSignal(signal.SIGINT)


    async def kill_sleep(seconds):
        try:
            return await asyncio.wait_for(terminateEvent.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            return False


    async def main():
        setup()
        while not await kill_sleep(schedule.idle_seconds()):  # will sleep until next
            schedule.run_pending()


    asyncio.run(main())


DrawBacks
----------
Only drawback is precision of asyncio.wait_for timeout.