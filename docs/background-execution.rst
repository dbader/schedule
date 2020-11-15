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


