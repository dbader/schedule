#!/usr/bin/env python3

import sys
import time
import datetime
import logging
import functools
import schedule


logger = logging.getLogger(__name__)

def setup_logging(debug=False, filename=sys.stderr, fmt=None):
    """
    Can be imported by ``<my_package>`` to create a log file for logging
    ``<my_package>`` class output.  In this example we use a ``debug``
    flag set in ``<my_package>`` to change the Log Level and ``filename``
    to set log path.  We also use UTC time and force the name in ``datefmt``.
    """
    if debug:
        log_level = logging.getLevelName('DEBUG')
    else:
        log_level = logging.getLevelName('INFO')

    # process format:
    #   '%(asctime)s %(name)s[%(process)d] %(levelname)s - %(message)s'
    # alt format
    #   '%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s'
    # long format
    #   '%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)s [%(process)d] %(message)s'
    format = '%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)s [%(process)d] %(message)s'

    if not fmt:
        fmt = format

    logging.basicConfig(level=log_level,
                        format=fmt,
                        datefmt='%Y-%m-%d %H:%M:%S UTC',
                        filename=filename)

    # BUG: This does not print the TZ name because logging module uses
    #      time instead of tz-aware datetime objects (so we force the
    #      correct name in datefmt above).
    logging.Formatter.converter = time.gmtime

    # To also log parent info, try something like this
    # global logger
    # logger = logging.getLogger("my_package")


def show_job_tags():
    def show_job_tags_decorator(job_func):
        """
        decorator to show job name and tags for current job
        """
        import schedule

        @functools.wraps(job_func)
        def job_tags(*args, **kwargs):
            current_job = min(job for job in schedule.jobs)
            job_tags = current_job.tags
            logger.info('JOB: {}'.format(current_job))
            logger.info('TAGS: {}'.format(job_tags))
            return job_func(*args, **kwargs)
        return job_tags
    return show_job_tags_decorator


def run_until_success(max_retry=2):
    """
    decorator for running a single job until success with retry limit
    * will unschedule itself on success
    * will reschedule on failure until max retry is exceeded
    :requirements:
    * the job function must return something to indicate success/failure
      or raise an exception on non-success
    :param max_retry: max number of times to reschedule the job on failure,
                      balance this with the job interval for best results
    """
    import schedule

    def run_until_success_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            current = min(job for job in schedule.jobs)
            num_try = int(max((tag for tag in current.tags if tag.isdigit()), default=0))
            tries_left = max_retry - num_try
            next_try = num_try + 1

            try:
                result = job_func(*args, **kwargs)

            except Exception as exc:
                # import traceback
                import warnings
                result = None
                logger.debug('JOB: {} failed on try number: {}'.format(current, num_try))
                warnings.warn('{}'.format(exc), RuntimeWarning, stacklevel=2)
                # logger.error('JOB: exception is: {}'.format(exc))
                # logger.error(traceback.format_exc())

            finally:
                if result:
                    logger.debug('JOB: {} claims success: {}'.format(current, result))
                    return schedule.CancelJob
                elif tries_left == 0:
                    logger.warning('JOB: {} failed with result: {}'.format(current, result))
                    return schedule.CancelJob
                else:
                    logger.debug('JOB: {} failed with {} try(s) left, trying again'.format(current, tries_left))
                    current.tags.update(str(next_try))
                    return result

        return wrapper
    return run_until_success_decorator


def catch_exceptions(cancel_on_failure=False):
    """
    decorator for running a suspect job with cancel_on_failure option
    """
    import schedule

    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                logger.debug(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


@show_job_tags()
@run_until_success()
def good_task():
    print('I am good')
    return True


@run_until_success()
def good_returns():
    print("I'm good too")
    return True, 'Success', 0


@run_until_success()
def bad_returns():
    print("I'm not so good")
    return 0


@show_job_tags()
@catch_exceptions(cancel_on_failure=True)
def bad_task():
    print('I am bad')
    raise Exception('Something went wrong!')


setup_logging(debug=True, filename='scheduler_check.log', fmt=None)

schedule.every(3).seconds.do(good_task).tag('1')
schedule.every(5).seconds.do(good_task).tag('good')
schedule.every(8).seconds.do(bad_task).tag('bad')
schedule.every(3).seconds.do(good_returns)
schedule.every(5).seconds.do(bad_returns)

have_jobs = len(schedule.jobs)
print(f'We have {have_jobs} jobs!')

while have_jobs > 0:
    schedule.run_pending()
    time.sleep(1)
    have_jobs = len(schedule.jobs)
