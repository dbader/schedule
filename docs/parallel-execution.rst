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

Queued jobs with arguments
-------------------------

The queue stores zero-argument callables for the worker to execute. Bind a
job's positional and keyword arguments with ``functools.partial`` before
putting it on the queue:

.. code-block:: python

    >>> from functools import partial
    >>> import queue
    >>> import schedule
    >>> def greet(name, punctuation="!"):
    ...     print("Hello, " + name + punctuation)
    >>> jobqueue = queue.Queue()
    >>> scheduler = schedule.Scheduler()
    >>> queued_job = scheduler.every(10).seconds.do(
    ...     jobqueue.put, partial(greet, "Alice", punctuation="."))

Passing arguments after ``jobqueue.put`` in ``do()`` sends them to
``Queue.put`` itself, whose additional arguments control blocking and timeouts.
The partial is instead passed as the single queue item. It does not call the
job until the worker invokes it.

This finite example enqueues one run and consumes it using the same callable
convention as the worker above:

.. code-block:: python

    >>> scheduler.run_all()
    >>> task = jobqueue.get_nowait()
    >>> try:
    ...     task()
    ... finally:
    ...     jobqueue.task_done()
    Hello, Alice.
    >>> jobqueue.empty()
    True

In an application, use ``run_pending()`` in the scheduler loop and let the
workers consume the queue. Calling ``task_done()`` in ``finally`` accounts for
failed jobs too; catch and report exceptions in the worker if it should keep
running after a job fails.

Create a partial inside each loop iteration when queuing different arguments,
for example ``partial(greet, name)``. Bound mutable values are shared by
reference, so copy them explicitly if each queued job needs a snapshot.
Workers execute the bound function outside Schedule: returning ``CancelJob``
from that function does not cancel the scheduled enqueue operation.
