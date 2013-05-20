schedule
========

Python job scheduling for humans. Inspired by `Adam Wiggins' <https://github.com/adamwiggins>`_ `clockwork <https://github.com/tomykaira/clockwork>`_.

Installation
------------

.. code-block:: bash

    $ pip install schedule

Usage
-----

.. code-block:: python

    import schedule

    def job():
        print("I'm working...")

    schedule.every(10).minutes.do(job)
    schedule.every().hour.do(job)
    schedule.every().day.at("10:30").do(job)

    while 1:
        schedule.run_pending()
        time.sleep(1)

Meta
----------
Daniel Bader – mail@dbader.org

Distributed under the MIT license. See LICENSE.txt for more information.

https://github.com/dbader/schedule
