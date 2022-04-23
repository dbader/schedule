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

ModuleNotFoundError: ModuleNotFoundError: No module named 'pytz'
----------------------------------------------------------------

This error happens when you try to set a timezone in ``.at()`` without having the `pytz <https://pypi.org/project/pytz/>`_ package installed.
Pytz is a required dependency when working with timezones.
To resolve this issue, install the ``pytz`` module by running ``pip install pytz``.

Does schedule support time zones?
---------------------------------
Yes! See :doc:`Timezones <timezones>`.

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

Another question?
-----------------
If you are left with an unanswered question, `browse the issue tracker <http://github.com/dbader/schedule/issues>`_ to see if your question has been asked before.
Feel free to create a new issue if that's not the case. Thank you 😃