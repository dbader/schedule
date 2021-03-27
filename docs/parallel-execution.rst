Parallel execution
==========================

*I am trying to execute 50 items every 10 seconds, but from the my logs it says it executes every item in 10 second schedule serially, is there a work around?*

By default, schedule executes all jobs serially. The reasoning behind this is that it would be difficult to find a model for parallel execution that makes everyone happy.

You can work around this limitation by running each of the jobs in its own thread:

.. code-block:: python

    import threading
    import time
    import schedule

    def job():
        print("I'm running on thread %s" % threading.current_thread())

    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()

    schedule.every(10).seconds.do(run_threaded, job)
    schedule.every(10).seconds.do(run_threaded, job)
    schedule.every(10).seconds.do(run_threaded, job)
    schedule.every(10).seconds.do(run_threaded, job)
    schedule.every(10).seconds.do(run_threaded, job)


    while 1:
        schedule.run_pending()
        time.sleep(1)

If you want tighter control on the number of threads use a shared jobqueue and one or more worker threads:

.. code-block:: python

    import time
    import threading
    import schedule
    import queue

    def job():
        print("I'm working")


    def worker_main():
        while 1:
            job_func = jobqueue.get()
            job_func()
            jobqueue.task_done()

    jobqueue = queue.Queue()

    schedule.every(10).seconds.do(jobqueue.put, job)
    schedule.every(10).seconds.do(jobqueue.put, job)
    schedule.every(10).seconds.do(jobqueue.put, job)
    schedule.every(10).seconds.do(jobqueue.put, job)
    schedule.every(10).seconds.do(jobqueue.put, job)

    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()

    while 1:
        schedule.run_pending()
        time.sleep(1)

This model also makes sense for a distributed application where the workers are separate processes that receive jobs from a distributed work queue. I like using beanstalkd with the beanstalkc Python library.
