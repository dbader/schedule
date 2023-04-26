"""
Largely inspired by Celery's https://github.com/celery/celery/blob/main/celery/schedules.py
"""

from typing import Any, Optional
import numbers
import re
from bisect import bisect, bisect_left
from collections.abc import Iterable
from datetime import datetime, timedelta, date
from calendar import monthrange

import pytz

DAYNAMES = "sun", "mon", "tue", "wed", "thu", "fri", "sat"
WEEKDAYS = dict(zip(DAYNAMES, range(7)))

CRON_PATTERN_INVALID = """\
Invalid crontab pattern.  Valid range is {min}-{max}. \
'{value}' was found.\
"""

CRON_INVALID_TYPE = """\
Argument cronspec needs to be of any of the following types: \
int, str, or an iterable type. {type!r} was given.\
"""

CRON_REPR = """\
<crontab: {0._orig_minute} {0._orig_hour} {0._orig_day_of_week} \
{0._orig_day_of_month} {0._orig_month_of_year} (m/h/d/dM/MY)>\
"""


class AttributeDict(dict):
    """Dict subclass with attribute access."""

    def __getattr__(self, k):
        # type: (str) -> Any
        """`d.key -> d[key]`."""
        try:
            return self[k]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {k!r}"
            )

    def __setattr__(self, key, value):
        # type: (str, Any) -> None
        """`d[key] = value -> d.key = value`."""
        self[key] = value


def cronfield(s):
    return "*" if s is None else s


def dictfilter(d=None, **kw):
    """Remove all keys from dict ``d`` whose value is :const:`None`."""
    d = kw if d is None else (dict(d, **kw) if kw else d)
    return {k: v for k, v in d.items() if v is not None}


class ParseException(Exception):
    """Raised by :class:`crontab_parser` when the input can't be parsed."""


def weekday(name):
    """Return the position of a weekday: 0 - 7, where 0 is Sunday.

    Example:
        >>> weekday('sunday'), weekday('sun'), weekday('mon')
        (0, 0, 1)
    """
    abbreviation = name[0:3].lower()
    try:
        return WEEKDAYS[abbreviation]
    except KeyError:
        # Show original day name in exception, instead of abbr.
        raise KeyError(name)


class CrontabParser:
    """Parser for Crontab expressions.

    Any expression of the form 'groups'
    (see BNF grammar below) is accepted and expanded to a set of numbers.
    These numbers represent the units of time that the Crontab needs to
    run on:

    .. code-block:: bnf

        digit   :: '0'..'9'
        dow     :: 'a'..'z'
        number  :: digit+ | dow+
        steps   :: number
        range   :: number ( '-' number ) ?
        numspec :: '*' | range
        expr    :: numspec ( '/' steps ) ?
        groups  :: expr ( ',' expr ) *

    The parser is a general purpose one, useful for parsing hours, minutes and
    day of week expressions.  Example usage:

    .. code-block:: pycon

        >>> minutes = CrontabParser(60).parse('*/15')
        [0, 15, 30, 45]
        >>> hours = CrontabParser(24).parse('*/4')
        [0, 4, 8, 12, 16, 20]
        >>> day_of_week = CrontabParser(7).parse('*')
        [0, 1, 2, 3, 4, 5, 6]

    It can also parse day of month and month of year expressions if initialized
    with a minimum of 1.  Example usage:

    .. code-block:: pycon

        >>> days_of_month = CrontabParser(31, 1).parse('*/3')
        [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]
        >>> months_of_year = CrontabParser(12, 1).parse('*/2')
        [1, 3, 5, 7, 9, 11]
        >>> months_of_year = CrontabParser(12, 1).parse('2-12/2')
        [2, 4, 6, 8, 10, 12]

    The maximum possible expanded value returned is found by the formula:

        :math:`max_ + min_ - 1`
    """

    ParseException = ParseException

    _range = r"(\w+?)-(\w+)"
    _steps = r"/(\w+)?"
    _star = r"\*"

    def __init__(self, max_=60, min_=0):
        self.max_ = max_
        self.min_ = min_
        self.pats = (
            (re.compile(self._range + self._steps), self._range_steps),
            (re.compile(self._range), self._expand_range),
            (re.compile(self._star + self._steps), self._star_steps),
            (re.compile("^" + self._star + "$"), self._expand_star),
        )

    def parse(self, spec):
        acc = set()
        for part in spec.split(","):
            if not part:
                raise self.ParseException("empty part")
            acc |= set(self._parse_part(part))
        return acc

    def _parse_part(self, part):
        for regex, handler in self.pats:
            m = regex.match(part)
            if m:
                return handler(m.groups())
        return self._expand_range((part,))

    def _expand_range(self, toks):
        fr = self._expand_number(toks[0])
        if len(toks) > 1:
            to = self._expand_number(toks[1])
            if to < fr:  # Wrap around max_ if necessary
                return list(range(fr, self.min_ + self.max_)) + list(
                    range(self.min_, to + 1)
                )
            return list(range(fr, to + 1))
        return [fr]

    def _range_steps(self, toks):
        if len(toks) != 3 or not toks[2]:
            raise self.ParseException("empty filter")
        return self._expand_range(toks[:2])[:: int(toks[2])]

    def _star_steps(self, toks):
        if not toks or not toks[0]:
            raise self.ParseException("empty filter")
        return self._expand_star()[:: int(toks[0])]

    def _expand_star(self, *args):
        return list(range(self.min_, self.max_ + self.min_))

    def _expand_number(self, s):
        if isinstance(s, str) and s[0] == "-":
            raise self.ParseException("negative numbers not supported")
        try:
            i = int(s)
        except ValueError:
            try:
                i = weekday(s)
            except KeyError:
                raise ValueError(f"Invalid weekday literal {s!r}.")

        max_val = self.min_ + self.max_ - 1
        if i > max_val:
            raise ValueError(f"Invalid end range: {i} > {max_val}.")
        if i < self.min_:
            raise ValueError(f"Invalid beginning range: {i} < {self.min_}.")

        return i


class Crontab:
    """Crontab schedule.

    Like a :manpage:`cron(5)`-job, you can specify units of time of when
    you'd like the job to execute.  It's a reasonably complete
    implementation of :command:`cron`'s features, so it should provide a fair
    degree of scheduling needs.

    You can specify a minute, an hour, a day of the week, a day of the
    month, and/or a month in the year in any of the following formats:

    .. attribute:: minute

        - A (list of) integers from 0-59 that represent the minutes of
          an hour of when execution should occur; or
        - A string representing a Crontab pattern.  This may get pretty
          advanced, like ``minute='*/15'`` (for every quarter) or
          ``minute='1,13,30-45,50-59/2'``.

    .. attribute:: hour

        - A (list of) integers from 0-23 that represent the hours of
          a day of when execution should occur; or
        - A string representing a Crontab pattern.  This may get pretty
          advanced, like ``hour='*/3'`` (for every three hours) or
          ``hour='0,8-17/2'`` (at midnight, and every two hours during
          office hours).

    .. attribute:: day_of_week

        - A (list of) integers from 0-6, where Sunday = 0 and Saturday =
          6, that represent the days of a week that execution should
          occur.
        - A string representing a Crontab pattern.  This may get pretty
          advanced, like ``day_of_week='mon-fri'`` (for weekdays only).
          (Beware that ``day_of_week='*/2'`` does not literally mean
          'every two days', but 'every day that is divisible by two'!)

    .. attribute:: day_of_month

        - A (list of) integers from 1-31 that represents the days of the
          month that execution should occur.
        - A string representing a Crontab pattern.  This may get pretty
          advanced, such as ``day_of_month='2-30/2'`` (for every even
          numbered day) or ``day_of_month='1-7,15-21'`` (for the first and
          third weeks of the month).

    .. attribute:: month_of_year

        - A (list of) integers from 1-12 that represents the months of
          the year during which execution can occur.
        - A string representing a Crontab pattern.  This may get pretty
          advanced, such as ``month_of_year='*/3'`` (for the first month
          of every quarter) or ``month_of_year='2-12/2'`` (for every even
          numbered month).


    It's important to realize that any day on which execution should
    occur must be represented by entries in all three of the day and
    month attributes.  For example, if ``day_of_week`` is 0 and
    ``day_of_month`` is every seventh day, only months that begin
    on Sunday and are also in the ``month_of_year`` attribute will have
    execution events.  Or, ``day_of_week`` is 1 and ``day_of_month``
    is '1-7,15-21' means every first and third Monday of every month
    present in ``month_of_year``.
    """

    def __init__(
        self,
        minute="*",
        hour="*",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        tz: Optional[str] = None,
        **kwargs,
    ):
        self._orig_minute = cronfield(minute)
        self._orig_hour = cronfield(hour)
        self._orig_day_of_week = cronfield(day_of_week)
        self._orig_day_of_month = cronfield(day_of_month)
        self._orig_month_of_year = cronfield(month_of_year)
        self._orig_kwargs = kwargs
        self.hour = self._expand_cronspec(hour, 24)
        self.minute = self._expand_cronspec(minute, 60)
        self.day_of_week = self._expand_cronspec(day_of_week, 7)
        self.day_of_month = self._expand_cronspec(day_of_month, 31, 1)
        self.month_of_year = self._expand_cronspec(month_of_year, 12, 1)
        self.tz = None
        if tz is not None:
            if isinstance(tz, str):
                self.tz = pytz.timezone(tz)  # type: ignore
            elif isinstance(tz, pytz.BaseTzInfo):
                self.tz = tz
            else:
                raise ValueError(
                    "Timezone must be string or pytz.timezone object"
                )

    @classmethod
    def from_expression(
        cls, crontab_expression: str, tz: Optional[str] = None
    ) -> "Crontab":
        items = crontab_expression.split(" ")
        if len(items) != 5:
            raise ValueError(
                "Invalid number of components in crontab expression"
            )

        return cls(
            minute=items[0],
            hour=items[1],
            day_of_week=items[2],
            day_of_month=items[3],
            month_of_year=items[4],
            tz=tz,
        )

    @staticmethod
    def _expand_cronspec(cronspec, max_, min_=0):
        """Expand cron specification.

        Takes the given cronspec argument in one of the forms:

        .. code-block:: text

            int         (like 7)
            str         (like '3-5,*/15', '*', or 'monday')
            set         (like {0,15,30,45}
            list        (like [8-17])

        And convert it to an (expanded) set representing all time unit
        values on which the Crontab triggers.  Only in case of the base
        type being :class:`str`, parsing occurs.  (It's fast and
        happens only once for each Crontab instance, so there's no
        significant performance overhead involved.)

        For the other base types, merely Python type conversions happen.

        The argument ``max_`` is needed to determine the expansion of
        ``*`` and ranges.  The argument ``min_`` is needed to determine
        the expansion of ``*`` and ranges for 1-based cronspecs, such as
        day of month or month of year.  The default is sufficient for minute,
        hour, and day of week.
        """
        if isinstance(cronspec, numbers.Integral):
            result = {cronspec}
        elif isinstance(cronspec, str):
            result = CrontabParser(max_, min_).parse(cronspec)
        elif isinstance(cronspec, set):
            result = cronspec
        elif isinstance(cronspec, Iterable):
            result = set(cronspec)
        else:
            raise TypeError(CRON_INVALID_TYPE.format(type=type(cronspec)))

        # assure the result does not preceed the min or exceed the max
        for number in result:
            if number >= max_ + min_ or number < min_:
                raise ValueError(
                    CRON_PATTERN_INVALID.format(
                        min=min_, max=max_ - 1 + min_, value=number
                    )
                )
        return result

    def _delta_to_next(self, last_run_at, next_hour, next_minute):
        """Find next delta.

        Takes a :class:`~datetime.datetime` of last run, next minute and hour,
        and returns a :class:`~celery.utils.time.ffwd` for the next
        scheduled day and time.

        Only called when ``day_of_month`` and/or ``month_of_year``
        cronspec is specified to further limit scheduled job execution.
        """
        datedata = AttributeDict(year=last_run_at.year)
        days_of_month = sorted(self.day_of_month)
        months_of_year = sorted(self.month_of_year)

        def day_out_of_range(year, month, day):
            try:
                datetime(year=year, month=month, day=day)
            except ValueError:
                return True
            return False

        def is_before_last_run(year, month, day):
            return (
                self._check_awareness(datetime(year, month, day)) < last_run_at
            )

        def roll_over():
            for _ in range(2000):
                flag = (
                    datedata.dom == len(days_of_month)
                    or day_out_of_range(
                        datedata.year,
                        months_of_year[datedata.moy],
                        days_of_month[datedata.dom],
                    )
                    or (
                        is_before_last_run(
                            datedata.year,
                            months_of_year[datedata.moy],
                            days_of_month[datedata.dom],
                        )
                    )
                )

                if flag:
                    datedata.dom = 0
                    datedata.moy += 1
                    if datedata.moy == len(months_of_year):
                        datedata.moy = 0
                        datedata.year += 1
                else:
                    break
            else:
                # Tried 2000 times, we're most likely in an infinite loop
                raise RuntimeError(
                    "unable to rollover, "
                    "time specification is probably invalid"
                )

        if last_run_at.month in self.month_of_year:
            datedata.dom = bisect(days_of_month, last_run_at.day)
            datedata.moy = bisect_left(months_of_year, last_run_at.month)
        else:
            datedata.dom = 0
            datedata.moy = bisect(months_of_year, last_run_at.month)
            if datedata.moy == len(months_of_year):
                datedata.moy = 0
        roll_over()

        while 1:
            th = datetime(
                year=datedata.year,
                month=months_of_year[datedata.moy],
                day=days_of_month[datedata.dom],
            )
            if th.isoweekday() % 7 in self.day_of_week:
                break
            datedata.dom += 1
            roll_over()

        return Ffwd(
            year=datedata.year,
            month=months_of_year[datedata.moy],
            day=days_of_month[datedata.dom],
            hour=next_hour,
            minute=next_minute,
            second=0,
            microsecond=0,
        )

    def __repr__(self):
        return CRON_REPR.format(self)

    def __reduce__(self):
        return (
            self.__class__,
            (
                self._orig_minute,
                self._orig_hour,
                self._orig_day_of_week,
                self._orig_day_of_month,
                self._orig_month_of_year,
            ),
            self._orig_kwargs,
        )

    def __setstate__(self, state):
        # Calling super's init because the kwargs aren't necessarily passed in
        # the same form as they are stored by the superclass
        super().__init__(**state)

    def now(self) -> datetime:
        if self.tz is None:
            return datetime.now()

        utcnow = datetime.now(pytz.UTC)
        return utcnow.astimezone(self.tz)

    def _check_awareness(self, dt: datetime) -> datetime:
        is_naive = dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None
        if is_naive:
            if self.tz is not None:
                ValueError(
                    "You cannot use naive datetime if the crontab is defined with a timezone"
                )
        else:
            if self.tz is None:
                ValueError(
                    "You cannot use localized datetime if the crontab is defined without a timezone"
                )
            else:
                dt = dt.astimezone(self.tz)
        return dt

    def next_run_time(self, last_run_at: Optional[datetime] = None):

        last_run_at = self._check_awareness(last_run_at or self.now())
        now = self._check_awareness(self.now())
        dow_num = last_run_at.isoweekday() % 7  # Sunday is day 0, not day 7

        execute_this_date = (
            last_run_at.month in self.month_of_year
            and last_run_at.day in self.day_of_month
            and dow_num in self.day_of_week
        )

        execute_this_hour = (
            execute_this_date
            and last_run_at.day == now.day
            and last_run_at.month == now.month
            and last_run_at.year == now.year
            and last_run_at.hour in self.hour
            and last_run_at.minute < max(self.minute)
        )

        if execute_this_hour:
            next_minute = min(
                minute for minute in self.minute if minute > last_run_at.minute
            )
            delta = Ffwd(minute=next_minute, second=0, microsecond=0)
        else:
            next_minute = min(self.minute)
            execute_today = execute_this_date and last_run_at.hour < max(
                self.hour
            )

            if execute_today:
                next_hour = min(
                    hour for hour in self.hour if hour > last_run_at.hour
                )
                delta = Ffwd(
                    hour=next_hour, minute=next_minute, second=0, microsecond=0
                )
            else:
                next_hour = min(self.hour)
                all_dom_moy = (
                    self._orig_day_of_month == "*"
                    and self._orig_month_of_year == "*"
                )
                if all_dom_moy:
                    next_day = min(
                        [day for day in self.day_of_week if day > dow_num]
                        or self.day_of_week
                    )
                    add_week = next_day == dow_num

                    delta = Ffwd(
                        weeks=add_week and 1 or 0,
                        weekday=(next_day - 1) % 7,
                        hour=next_hour,
                        minute=next_minute,
                        second=0,
                        microsecond=0,
                    )
                else:
                    delta = self._delta_to_next(
                        last_run_at, next_hour, next_minute
                    )
        next_run_at = now + delta
        if self.tz:
            next_run_at = self.tz.normalize(next_run_at)
        return next_run_at

    def __eq__(self, other):
        if isinstance(other, Crontab):
            return (
                other.month_of_year == self.month_of_year
                and other.day_of_month == self.day_of_month
                and other.day_of_week == self.day_of_week
                and other.hour == self.hour
                and other.minute == self.minute
                and super().__eq__(other)
            )
        return NotImplemented

    def __ne__(self, other):
        res = self.__eq__(other)
        if res is NotImplemented:
            return True
        return not res


class Ffwd:
    """Version of ``dateutil.relativedelta`` that only supports addition."""

    def __init__(
        self,
        year=None,
        month=None,
        weeks=0,
        weekday=None,
        day=None,
        hour=None,
        minute=None,
        second=None,
        microsecond=None,
        **kwargs,
    ):
        # pylint: disable=redefined-outer-name
        # weekday is also a function in outer scope.
        self.year = year
        self.month = month
        self.weeks = weeks
        self.weekday = weekday
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        self.days = weeks * 7
        self._has_time = self.hour is not None or self.minute is not None

    def __radd__(self, other):
        if not isinstance(other, date):
            return NotImplemented
        year = self.year or other.year
        month = self.month or other.month
        day = min(monthrange(year, month)[1], self.day or other.day)
        ret = other.replace(
            **dict(dictfilter(self._fields()), year=year, month=month, day=day)
        )
        if self.weekday is not None:
            ret += timedelta(days=(7 - ret.weekday() + self.weekday) % 7)
        return ret + timedelta(days=self.days)

    def _fields(self, **extra):
        return dictfilter(
            {
                "year": self.year,
                "month": self.month,
                "day": self.day,
                "hour": self.hour,
                "minute": self.minute,
                "second": self.second,
                "microsecond": self.microsecond,
            },
            **extra,
        )
