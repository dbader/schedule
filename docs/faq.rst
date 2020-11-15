Frequently Asked Questions
==========================

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

Did you install schedule? If not, follow :doc:`installation`.
If you installed using pip, validate the installation by running ``pip3 list | grep schedule``.

Are you using the same Python version to install Schedule and execute your code?
For example, if you installed schedule using a version of pip that uses Python 2, and your code runs in Python 3, the package won't be found.
In this case the solution is to install Schedule using pip3: ``pip3 install schedule``.

Are you using virtualenv? Check that you are running the script inside the same virtualenv where you installed schedule.

Is this problem occurring when running the program from inside and IDE like PyCharm or VSCode?
Try to run your program from a commandline outside of the IDE.
If it works there, the problem is in your IDE configuration.
It might be that your IDE uses a different Python interpreter installation.

Still having problems? Use Google and StackOverflow before submitting an issue.