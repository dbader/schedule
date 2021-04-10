Asyncio examples with events and signals
========================================


Those examples how python asyncio facilities may interact with schedule.
It will touch Terminate-able loop, handling signals and changing sleep time due scheduling during sleep.

Terminate-able loop
-------------
.. code-block:: python
    import schedule
    import asyncio

    event=None

    async def terminator():
        print("I will be back")
        await asyncio.sleep(1)
        event.set()

    schedule.every(5).seconds.do(lambda: asyncio.create_task(terminator()))

    async def sleep(seconds):
        if seconds is None:
            return True #no more jobs, terminate
        if seconds==0:
            return False
        try:
            return await asyncio.wait_for(event.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            return False


    async def scheduler():
        global event
        event=asyncio.Event()
        while not await sleep(schedule.idle_seconds()):  # will sleep until next or exits
            schedule.run_pending()


    asyncio.run(scheduler())

 Save Scheduling during sleep
-----------------------------
.. code-block:: python
    import schedule
    import asyncio

    event = None


    # this can even be called from another threads but you must have loop that schedule loop is running on
    # it can be done like   loop.call_soon_threadsafe(async_schedule,schedule_call)
    # this is threadsafe thanks to cooperative multitasking (newer multiple async_schedule are running at same time)
    def async_schedule(*schedule_calls):
        next_run = schedule.next_run()
        for call in schedule_calls:
            call()
        if next_run != schedule.next_run():
            event.set()


    def submit_once():
        async def late_submit():
            await asyncio.sleep(1)#submiting during sleep
            print("submiting new task")
            async_schedule(lambda: schedule.every(2).seconds.do(lambda: print("new  task running")))

        asyncio.create_task(late_submit())
        return schedule.CancelJob


    schedule.every(1).seconds.do(submit_once)


    schedule.every(8).seconds.do(lambda: print("keep loop working"))


    async def scheduler():
        global event
        event = asyncio.Event()
        interrupt_task = asyncio.create_task(event.wait())
        seconds = schedule.idle_seconds()
        while seconds is not None:# if seconds is None there are no other jobs
            if seconds > 0:
                done, _ = await asyncio.wait({interrupt_task}, timeout=seconds)
                if interrupt_task in done:  # someone set event
                    event.clear()
                    interrupt_task = asyncio.create_task(event.wait()) #start monitoring again
                    seconds = schedule.idle_seconds()
                    continue  # re-schedule


            schedule.run_pending()
            seconds = schedule.idle_seconds()


    asyncio.run(scheduler())



Termination on os signals
--------------------------
.. code-block:: python
    import schedule
    import asyncio
    print(schedule.every().wednesday.do(lambda: print("It is Wednesday...")))

    print(schedule.every().sunday.do(lambda: asyncio.create_task(something_useful)))
    terminateEvent = None
    def setup(): #needs to run on asyncio loop and setup on main thread
        import signal
        global terminateEvent
        terminateEvent = asyncio.Event() #needs to run on asyncio loop
        def terminate(signum):
            print(f"sayonara, I received {signum}")
            terminateEvent.set()  # kill loop

        loop = asyncio.get_running_loop() #needs to run on asyncio loop
        def handler(signum): # this is universal
            global handler # allows self modifying code
            try: #runtime probe if this python have add_signal_handler defined
                loop.add_signal_handler(signum, lambda:terminate(signum))
                def simplified(signum):#yay it has lets remove try catch to simplify it on next run
                    loop.add_signal_handler(signum, lambda:terminate(signum))
                 handler=simplified
            except NotImplementedError: #not defined lets use self modifying code to execute correct version on next run
                def backup_handler(signum):
                    orig_impl=signal.getsignal(signalnum)
                    if not orig_impl:
                        orig_impl = signal.SIG_IGN
                    def wrapper(sig, frame):
                        terminate(sig)
                        orig_impl(sig, frame)
                    signal.signal(signum, wrapper)
                handler = backup_handler
                backup_handler(signum)
            finally:
                handler.__name__="handler"

            handler(signal.SIGINT)

      async def sleep(seconds):
        if seconds is None:
            return True #no more jobs, terminate
        if seconds==0:
            return False
        try:
            return await asyncio.wait_for(event.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            return False

    async def main():
        setup()
        while not await sleep(schedule.idle_seconds()):
            schedule.run_pending()
    asyncio.run(main())

