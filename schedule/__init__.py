import datetime
import functools
import random
import time
from typing import Callable, Hashable, List, Optional, Set


class ScheduleError(Exception):
    """Base class for all scheduling errors."""
    pass


class ScheduleValueError(ScheduleError):
    """Exception raised for invalid scheduling values."""
    pass


class IntervalError(ScheduleValueError):
    """Exception raised for invalid interval values."""
    pass


class CancelJob:
    """Represents a canceled job instance."""
    
    def __repr__(self) -> str:
        return "<CancelJob>"


class Job:
    def __init__(self, interval: int, scheduler: Optional['Scheduler'] = None):
        if interval <= 0:
            raise IntervalError("Interval must be a positive integer.")
        
        self.interval: int = interval
        self.latest: Optional[int] = None
        self.job_func: Optional[functools.partial] = None
        self.unit: Optional[str] = None
        self.at_time: Optional[datetime.time] = None
        self.at_time_zone: Optional[datetime.tzinfo] = None
        self.last_run: Optional[datetime.datetime] = None
        self.next_run: Optional[datetime.datetime] = None
        self.start_day: Optional[str] = None
        self.cancel_after: Optional[datetime.datetime] = None
        self.tags: Set[Hashable] = set()
        self.scheduler: Optional['Scheduler'] = scheduler
    
    def __lt__(self, other: 'Job') -> bool:
        return bool(self.next_run and other.next_run and self.next_run < other.next_run)
    
    def do(self, job_func: Callable, *args, **kwargs) -> 'Job':
        if not callable(job_func):
            raise ScheduleError("Job function must be callable.")
        
        self.job_func = functools.partial(job_func, *args, **kwargs)
        functools.update_wrapper(self.job_func, job_func)
        
        if not self.scheduler:
            raise ScheduleError("Job is not associated with a scheduler.")
        
        self._schedule_next_run()
        self.scheduler.jobs.append(self)
        return self
    
    def run(self):
        now = datetime.datetime.now()
        if self._is_overdue(now):
            return CancelJob()
        
        result = self.job_func() if self.job_func else None
        self.last_run = now
        self._schedule_next_run()
        
        return CancelJob() if self._is_overdue(self.next_run) else result
    
    def _schedule_next_run(self) -> None:
        if self.unit not in {"seconds", "minutes", "hours", "days", "weeks"}:
            raise ScheduleValueError("Invalid unit for scheduling.")
        
        interval = random.randint(self.interval, self.latest) if self.latest else self.interval
        now = datetime.datetime.now(self.at_time_zone)
        self.next_run = now + datetime.timedelta(**{self.unit: interval})
    
    def _is_overdue(self, when: Optional[datetime.datetime]) -> bool:
        return self.cancel_after is not None and when is not None and when > self.cancel_after


class Scheduler:
    def __init__(self):
        self.jobs: List[Job] = []
    
    def every(self, interval: int = 1) -> Job:
        return Job(interval, scheduler=self)
    
    def run_pending(self) -> None:
        now = datetime.datetime.now()
        for job in self.jobs[:]:
            if job.next_run and job.next_run <= now:
                job.run()
    
    def run_all(self, delay_seconds: int = 0) -> None:
        for job in self.jobs[:]:
            job.run()
            if delay_seconds:
                time.sleep(delay_seconds)
    
    def get_jobs(self, tag: Optional[Hashable] = None) -> List[Job]:
        return [job for job in self.jobs if not tag or tag in job.tags]
    
    def clear(self, tag: Optional[Hashable] = None) -> None:
        self.jobs = [job for job in self.jobs if tag and tag in job.tags] if tag else []
    
    def cancel_job(self, job: Job) -> None:
        if job in self.jobs:
            self.jobs.remove(job)
    
    def get_next_run(self, tag: Optional[Hashable] = None) -> Optional[datetime.datetime]:
        jobs = self.get_jobs(tag)
        return min((job.next_run for job in jobs if job.next_run), default=None)
    
    @property
    def idle_seconds(self) -> Optional[float]:
        next_run = self.get_next_run()
        return (next_run - datetime.datetime.now()).total_seconds() if next_run else None


default_scheduler = Scheduler()


def every(interval: int = 1) -> Job:
    return default_scheduler.every(interval)


def run_pending() -> None:
    default_scheduler.run_pending()


def run_all(delay_seconds: int = 0) -> None:
    default_scheduler.run_all(delay_seconds=delay_seconds)


def get_jobs(tag: Optional[Hashable] = None) -> List[Job]:
    return default_scheduler.get_jobs(tag)


def clear(tag: Optional[Hashable] = None) -> None:
    default_scheduler.clear(tag)


def cancel_job(job: Job) -> None:
    default_scheduler.cancel_job(job)


def next_run(tag: Optional[Hashable] = None) -> Optional[datetime.datetime]:
    return default_scheduler.get_next_run(tag)


def idle_seconds() -> Optional[float]:
    return default_scheduler.idle_seconds

from typing import List, Optional, Hashable
import datetime
import time
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self) -> None:
        self.jobs: List[Job] = []

    def run_pending(self) -> None:
        """Run all jobs that are scheduled to run."""
        jobs_to_run = sorted((job for job in self.jobs if job.should_run), key=lambda j: j.next_run)
        for job in jobs_to_run:
            self._run_job(job)

    def run_all(self, delay_seconds: int = 0) -> None:
        """Run all jobs, with an optional delay between each."""
        logger.debug("Running all %d jobs with %ds delay in between", len(self.jobs), delay_seconds)
        for job in self.jobs[:]:
            self._run_job(job)
            if delay_seconds > 0:
                time.sleep(delay_seconds)

    def get_jobs(self, tag: Optional[Hashable] = None) -> List["Job"]:
        """Retrieve all jobs, optionally filtered by tag."""
        return self.jobs if tag is None else [job for job in self.jobs if tag in job.tags]

    def clear(self, tag: Optional[Hashable] = None) -> None:
        """Clear all jobs or jobs matching a specific tag."""
        if tag is None:
            logger.debug("Deleting all jobs")
            self.jobs.clear()
        else:
            logger.debug("Deleting all jobs tagged '%s'", tag)
            self.jobs = [job for job in self.jobs if tag not in job.tags]

    def cancel_job(self, job: "Job") -> None:
        """Cancel a specific job if it exists in the schedule."""
        if job in self.jobs:
            self.jobs.remove(job)
            logger.debug("Cancelled job '%s'", job)
        else:
            logger.debug("Attempted to cancel non-scheduled job '%s'", job)

    def every(self, interval: int = 1) -> "Job":
        """Create a new job with the specified interval."""
        return Job(interval, self)

    def _run_job(self, job: "Job") -> None:
        """Execute a job and handle cancellation if necessary."""
        if isinstance((result := job.run()), CancelJob):
            self.cancel_job(job)

    def get_next_run(self, tag: Optional[Hashable] = None) -> Optional[datetime.datetime]:
        """Get the next scheduled run time of the earliest job."""
        jobs_filtered = self.get_jobs(tag)
        return min(jobs_filtered, key=lambda j: j.next_run).next_run if jobs_filtered else None

    next_run = property(get_next_run)

    @property
    def idle_seconds(self) -> Optional[float]:
        """Return the number of seconds until the next job runs."""
        return (self.next_run - datetime.datetime.now()).total_seconds() if self.next_run else None
