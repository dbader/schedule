.. :changelog:

History
-------

0.2.0 (unreleased)
++++++++++++++++++

- Fixed issue with 'at_time' jobs not running on the same day the job is created

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
