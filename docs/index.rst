schedule
========


.. image:: https://api.travis-ci.org/dbader/schedule.svg?branch=master
        :target: https://travis-ci.org/dbader/schedule

.. image:: https://coveralls.io/repos/dbader/schedule/badge.svg?branch=master
        :target: https://coveralls.io/r/dbader/schedule

.. image:: https://img.shields.io/pypi/v/schedule.svg
        :target: https://pypi.python.org/pypi/schedule

Python job scheduling for humans. Run Python functions (or any other callable) periodically using a friendly syntax.

- A simple to use API for scheduling jobs, made for humans.
- In-process scheduler for periodic jobs. No extra processes needed!
- Very lightweight and no external dependencies.
- Excellent test coverage.
- Tested on Python 2.7, 3.5, and 3.6


:doc:`Example <examples>`
-------------------------

.. code-block:: bash

    $ pip install schedule

.. code-block:: python

    import schedule
    import time

    def job():
        print("I'm working...")

    schedule.every(10).minutes.do(job)
    schedule.every().hour.do(job)
    schedule.every().day.at("10:30").do(job)
    schedule.every().monday.do(job)
    schedule.every().wednesday.at("13:15").do(job)
    schedule.every().minute.at(":17").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


More :doc:`examples`

**Schedule does not account for the time it takes the job function to execute.**
To guarantee a stable execution schedule you need to move long-running jobs off the main-thread (where the scheduler runs).
See :doc:`parallel-execution` for a sample implementation.


Read More
---------
.. toctree::
   :maxdepth: 2

   installation
   examples
   background-execution
   parallel-execution
   exception-handling
   logging
   multiple-schedulers
   faq
   reference
   development


Issues
------

If you encounter any problems, please `file an issue <http://github.com/dbader/schedule/issues>`_ along with a detailed description.
Please also use the search feature in the issue tracker beforehand to avoid creating duplicates. Thank you 😃

About Schedule
--------------

Created by `Daniel Bader <https://dbader.org/>`__ - `@dbader_org <https://twitter.com/dbader_org>`_

Inspired by `Adam Wiggins' <https://github.com/adamwiggins>`_ article `"Rethinking Cron" <https://adam.herokuapp.com/past/2010/4/13/rethinking_cron/>`_ and the `clockwork <https://github.com/Rykian/clockwork>`_ Ruby module.


Distributed under the MIT license. See ``LICENSE.txt`` for more information.

.. include:: ../AUTHORS.rst
