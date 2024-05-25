Run in the background
=====================

Out of the box it is not possible to run the schedule in the background.
However, you can create a thread yourself and use it to run jobs without blocking the main thread.
This is an example of how you could do this:

.. code-block:: python

    import threading
    import time

    import schedule


    def run_continuously(interval=1):
        """Continuously run, while executing pending jobs at each
        elapsed time interval.
        @return cease_continuous_run: threading. Event which can
        be set to cease continuous run. Please note that it is
        *intended behavior that run_continuously() does not run
        missed jobs*. For example, if you've registered a job that
        should run every minute and you set a continuous run
        interval of one hour then your job won't be run 60 times
        at each interval but only once.
        """
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run


    def background_job():
        print('Hello from the background thread')


    schedule.every().second.do(background_job)

    # Start the background thread
    stop_run_continuously = run_continuously()

    # Do some other things...
    time.sleep(10)

    # Stop the background thread
    stop_run_continuously.set()

This second example extends the Scheduler class and adds the ability to run the scheduler in its own thread.
It exposes two simple functions to start and stop the threaded scheduler.

.. code-block:: python

    import schedule, threading, time

    def job1():
        print("Job 1 " + str(time.time()))

    def job2():
        print("Job 2 " + str(time.time()))

    def job3():
        print("Job 3 " + str(time.time()))


    class SchedulerThread(schedule.Scheduler):
        """Expansion of the scheduler class enabling a scheduler to run in the background.
        The scheduler is run in a separate Thread.
        Stopping of the thread is realized via an event. 
        """

        __cease_continuous_run = threading.Event()

        def run_background(self, interval: int = 1):
            self.__background_thread = threading.Thread(target=self.__background_executor, args=(interval,))
            self.__background_thread.daemon = True
            self.__background_thread.start()

        def __background_executor(self, interval):
            while not self.__cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

        def stop_background(self):
            self.__cease_continuous_run.set()


    s = SchedulerThread()

    t1 = s.every(1).seconds.do(job1)
    t2 = s.every(2).seconds.do(job2)

    s.run_background()

    time.sleep(7)
    print("Starting job 3 and stopping job 1")
    t3 = s.every(1).second.do(job3)
    s.cancel_job(t1)

    time.sleep(5)
    print("Stopping the scheduler thread")
    s.stop_background()