.. :changelog:

History
-------


0.6.0 (2019-01-20)
++++++++++++++++++

- Make at() accept timestamps with 1 second precision (#267). Thanks @NathanWailes!
- Introduce proper exception hierarchy (#271). Thanks @ConnorSkees!


0.5.0 (2017-11-16)
++++++++++++++++++

- Keep partially scheduled jobs from breaking the scheduler (#125)
- Add support for random intervals (Thanks @grampajoe and @gilbsgilbs)


0.4.3 (2017-06-10)
++++++++++++++++++

- Improve docs & clean up docstrings


0.4.2 (2016-11-29)
++++++++++++++++++

- Publish to PyPI as a universal (py2/py3) wheel


0.4.0 (2016-11-28)
++++++++++++++++++

- Add proper HTML (Sphinx) docs available at https://schedule.readthedocs.io/
- CI builds now run against Python 2.7 and 3.5 (3.3 and 3.4 should work fine but are untested)
- Fixed an issue with ``run_all()`` and having more than one job that deletes itself in the same iteration. Thanks @alaingilbert.
- Add ability to tag jobs and to cancel jobs by tag. Thanks @Zerrossetto.
- Improve schedule docs. Thanks @Zerrossetto.
- Additional docs fixes by @fkromer and @yetingsky.

0.3.2 (2015-07-02)
++++++++++++++++++

- Fixed issues where scheduling a job with a functools.partial as the job function fails. Thanks @dylwhich.
- Fixed an issue where scheduling a job to run every >= 2 days would cause the initial execution to happen one day early. Thanks @WoLfulus for identifying this and providing a fix.
- Added a FAQ item to describe how to schedule a job that runs only once.

0.3.1 (2014-09-03)
++++++++++++++++++

- Fixed an issue with unicode handling in setup.py that was causing trouble on Python 3 and Debian (https://github.com/dbader/schedule/issues/27). Thanks to @waghanza for reporting it.
- Added an FAQ item to describe how to deal with job functions that throw exceptions. Thanks @mplewis.

0.3.0 (2014-06-14)
++++++++++++++++++

- Added support for scheduling jobs on specific weekdays. Example: ``schedule.every().tuesday.do(job)`` or ``schedule.every().wednesday.at("13:15").do(job)`` (Thanks @abultman.)
- Run tests against Python 2.7 and 3.4. Python 3.3 should continue to work but we're not actively testing it on CI anymore.

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
