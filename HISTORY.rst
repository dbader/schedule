.. :changelog:

History
-------

0.2.1 (2013-11-20)
++++++++++++++++++
- Fixed history (no code changes).

0.2.0 (2013-11-09)
++++++++++++++++++
- This release introduces two new features in a backwards compatible way:
- Allow jobs to cancel repeated execution: Jobs can be cancelled by calling ``schedule.cancel_job()`` or by returning ``schedule.CancelJob`` from the job function. (Thanks to @cfrco and @matrixise.)
- Updated ``at_time()`` to allow running jobs at a particular time every hour. Example: ``every().hour.at(':15').do(job)`` will run ``job`` 15 minutes after every full hour. (Thanks @mattss.)
- Refactored unit tests to mock ``datetime`` in a cleaner way. (Thanks @matts.)

0.1.11 (2013-07-30)
+++++++++++++++++++
- Fixed an issue with ``next_run()`` throwing a ``ValueError`` exception when the job queue is empty. Thanks to @dpagano for pointing this out and thanks to @mrhwick for quickly providing a fix.

0.1.10 (2013-06-07)
+++++++++++++++++++

- Fixed issue with ``at_time`` jobs not running on the same day the job is created (Thanks to @mattss)

0.1.9 (2013-05-27)
++++++++++++++++++

- Added ``schedule.next_run()``
- Added ``schedule.idle_seconds()``
- Args passed into ``do()`` are forwarded to the job function at call time
- Increased test coverage to 100%


0.1.8 (2013-05-21)
++++++++++++++++++

- Changed default ``delay_seconds`` for ``schedule.run_all()`` to 0 (from 60)
- Increased test coverage

0.1.7 (2013-05-20)
++++++++++++++++++

- API change: renamed ``schedule.run_all_jobs()`` to ``schedule.run_all()``
- API change: renamed ``schedule.run_pending_jobs()`` to ``schedule.run_pending()``
- API change: renamed ``schedule.clear_all_jobs()`` to ``schedule.clear()``
- Added ``schedule.jobs``

0.1.6 (2013-05-20)
++++++++++++++++++

- Fix packaging
- README fixes

0.1.4 (2013-05-20)
++++++++++++++++++

- API change: renamed ``schedule.tick()`` to ``schedule.run_pending_jobs()``
- Updated README and ``setup.py`` packaging

0.1.0 (2013-05-19)
++++++++++++++++++

- Initial release
