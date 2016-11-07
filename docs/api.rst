.. _api:

Developer Interface
===================

.. module:: schedule

This part of the documentation covers all the interfaces of schedule. For
parts where schedule depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

Main Interface
--------------

.. autodata:: default_scheduler
.. autodata:: jobs

.. autofunction:: every
.. autofunction:: run_pending
.. autofunction:: run_all
.. autofunction:: clear
.. autofunction:: cancel_job
.. autofunction:: next_run
.. autofunction:: idle_seconds

Exceptions
----------

.. autoexception:: schedule.CancelJob


Classes
-------

.. autoclass:: schedule.Scheduler
   :members:
   :undoc-members:

.. autoclass:: schedule.Job
   :members:
   :undoc-members:
