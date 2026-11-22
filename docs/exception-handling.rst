Exception Handling
##################

Schedule doesn't catch exceptions that happen during job execution. Therefore any exceptions thrown during job execution will bubble up and interrupt schedule's run_xyz function.

If you want to guard against exceptions you can wrap your job function
in a decorator like this:

.. code-block:: python

    import functools

    def catch_exceptions(cancel_on_failure=False):
        def catch_exceptions_decorator(job_func):
            @functools.wraps(job_func)
            def wrapper(*args, **kwargs):
                try:
                    return job_func(*args, **kwargs)
                except:
                    import traceback
                    print(traceback.format_exc())
                    if cancel_on_failure:
                        return schedule.CancelJob
            return wrapper
        return catch_exceptions_decorator

    @catch_exceptions(cancel_on_failure=True)
    def bad_task():
        return 1 / 0

    schedule.every(5).minutes.do(bad_task)

Another option would be to subclass Schedule like @mplewis did in `this example <https://gist.github.com/mplewis/8483f1c24f2d6259aef6>`_.

Cancel after consecutive failures
---------------------------------

To retry temporary failures on later scheduled runs and cancel after a fixed
number of consecutive failures, give each scheduled job its own wrapper:

.. code-block:: python

    >>> import functools
    >>> import logging
    >>> import schedule
    >>> def cancel_after_failures(job_func, limit, exceptions=(Exception,)):
    ...     if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
    ...         raise ValueError("limit must be a positive integer")
    ...     failures = 0
    ...     @functools.wraps(job_func)
    ...     def wrapper(*args, **kwargs):
    ...         nonlocal failures
    ...         try:
    ...             result = job_func(*args, **kwargs)
    ...         except exceptions:
    ...             failures += 1
    ...             logging.getLogger(__name__).exception("Scheduled job failed")
    ...             if failures >= limit:
    ...                 return schedule.CancelJob
    ...         else:
    ...             failures = 0
    ...             return result
    ...     return wrapper

For example, wrap a download separately for each registration::

    schedule.every(5).minutes.do(
        cancel_after_failures(download, 10, exceptions=(OSError,)),
        "https://example.org/data.csv",
    )

Each failed invocation counts as one attempt. A successful run resets the
counter; the next retry waits for the normal interval, with no additional
sleep or immediate retry loop. Exceptions outside the selected tuple still
propagate. The default catches ``Exception``, so ``KeyboardInterrupt`` and
``SystemExit`` are not swallowed. Successful return values, including
``CancelJob``, are preserved.

Call the factory again for each scheduled job so that failure counters are
independent. This recipe is for jobs executed directly by Schedule. A function
running in a separate worker thread or queue cannot cancel its scheduled
launcher merely by returning ``CancelJob``; arrange cancellation on the
scheduler side instead.
