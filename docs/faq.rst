Frequently Asked Questions
==========================

Frequently asked questions on the usage of schedule.
Did you get here using an 'old' link and expected to see more questions?

AttributeError: 'module' object has no attribute 'every'
--------------------------------------------------------

I'm getting

.. code-block:: text

    AttributeError: 'module' object has no attribute 'every'

when I try to use schedule.

This happens if your code imports the wrong ``schedule`` module.
Make sure you don't have a ``schedule.py`` file in your project that overrides the ``schedule`` module provided by this library.


ModuleNotFoundError: No module named 'schedule'
-----------------------------------------------

It seems python can't find the schedule package. Let's check some common causes.

Did you install schedule? If not, follow :doc:`installation`. Validate installation:

* Did you install using pip? Run ``pip3 list | grep schedule``. This should return ``schedule   0.6.0`` (or a higher version number)
* Did you install using apt? Run ``dpkg -l | grep python3-schedule``. This should return something along the lines of ``python3-schedule     0.3.2-1.1     Job scheduling for humans (Python 3)`` (or a higher version number)

Are you used python 3 to install Schedule, and are running the script using python 3?
For example, if you installed schedule using a version of pip that uses Python 2, and your code runs in Python 3, the package won't be found.
In this case the solution is to install Schedule using pip3: ``pip3 install schedule``.

Are you using virtualenv? Check that you are running the script inside the same virtualenv where you installed schedule.

Is this problem occurring when running the program from inside and IDE like PyCharm or VSCode?
Try to run your program from a commandline outside of the IDE.
If it works there, the problem is with your IDE configuration.
It might be that your IDE uses a different Python interpreter installation.

Still having problems? Use Google and StackOverflow before submitting an issue.

Does schedule support time zones?
---------------------------------
Vanilla schedule doesn’t support time zones at the moment.
If you need this functionality please check out @imiric’s work `here <https://github.com/dbader/schedule/pull/16>`_.
He added time zone support to schedule using python-dateutil.

What if my task throws an exception?
------------------------------------
See :doc:`Exception Handling <exception-handling>`.

How can I run a job only once?
------------------------------
See :doc:`Examples <examples>`.

How can I cancel several jobs at once?
--------------------------------------
See :doc:`Examples <examples>`.

How to execute jobs in parallel?
--------------------------------
See :doc:`Parallel Execution <parallel-execution>`.

How to continuously run the scheduler without blocking the main thread?
-----------------------------------------------------------------------
:doc:`Background Execution<background-execution>`.

Does schedule support asyncio coroutines?
-----------------------------------------
Schedule does not accept coroutines as jobs directly yet.
However, using using ``asyncio.create_task`` you able to schedule async jobs.
See :doc:`this page <async-support>` for an example.


Can i use threading.Event.wait as means of scheduling and Terminating loop with loong sleep?
----------------------------------------------------------------------------------------
Only in cases when you are running scheduling loop in separate thread
you also must make sure that you are not blocking main thread with joins/waiting on event etc.
This is because python will not handle any signals
However you can use ``asyncio.Event`` See :doc:`this page <async-events.signals>`

My long sleeping scheduler is not reacting on ctr+c
---------------------------------------------------
In your code or other dependencies there is somewhere overridden signal handler
without also calling previous implementation that means KeyboardInterrupt is no longer thrown
so you will have to override their signal handler with your that exits loop and execute their implementation if needed.

or you may be blocking main thread.

See :doc:`this page <async-events.signals>`.

What happens when my computer hibernates during time.sleep/wait
----------------------------------------------------------------
Depending on python version it may behave erratically in undocumented ways `see <https://bugs.python.org/issue43821?@ok_message=msg%20390914%20createdissue%2043821%20created&@template=item>`_
in future this may be resolved by asyncio

Another question?
-----------------
If you are left with an unanswered question, `browse the issue tracker <http://github.com/dbader/schedule/issues>`_ to see if your question has been asked before.
Feel free to create a new issue if that's not the case. Thank you 😃