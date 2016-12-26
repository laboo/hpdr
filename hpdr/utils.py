# pylint: disable=redefined-builtin

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from calendar import monthrange
from datetime import timedelta
import re
from builtins import int
from builtins import str
import attr
import pendulum
from future import standard_library
from hpdr import enums
from hpdr.enums import Level, Position
standard_library.install_aliases()

ZERO_BASED = {Level.HH, Level.MIN}

def _adjust(level, value):
    """Decrements a value by 1 iff it's not a zero-base value like HOUR (0-23)"""
    adjusted = value if level in ZERO_BASED else value - 1
    return adjusted

def _add_condition_to_datetimes(cnd, pos, early, late):
    """Determine the duration of time in a condition and add to it to early and late.

    For example, 'MM=02' is equal to one month of time (just February). But if the
    sign is not '=', then the duration depends of the Position of the condition.
    For example, 'MM>=02', if on the left, as in
    'MM>=02' is equal to 11 months (February through December)
    """
    level = level_to_datetime_unit(cnd.level)
    if cnd.sign == '=':
        early = add_to_datetime(early, level, _adjust(cnd.level, cnd.value))
        late = add_to_datetime(late, level, _adjust(cnd.level, cnd.value))

    elif pos == Position.left:
        if cnd.sign == '>':
            early = add_to_datetime(early, level, _adjust(cnd.level, cnd.value) + 1)
        elif cnd.sign == '>=':
            early = add_to_datetime(early, level, _adjust(cnd.level, cnd.value))
        late = add_to_datetime(late, level, _adjust(cnd.level, get_max(cnd.level, late) + 1))
    elif pos == Position.right:
        early = add_to_datetime(early, level, _adjust(cnd.level, get_min(cnd.level)))
        if cnd.sign == '<':
            late = add_to_datetime(late, level, _adjust(cnd.level, cnd.value))
        elif cnd.sign == '<=':
            late = add_to_datetime(late, level, _adjust(cnd.level, cnd.value) + 1)
    elif pos == Position.middle:
        if cnd.sign == '<':
            late = add_to_datetime(late, level, _adjust(cnd.level, cnd.value))
        elif cnd.sign == '>':
            early = add_to_datetime(early, level, _adjust(cnd.level, cnd.value) + 1)
        elif cnd.sign == '>=':
            early = add_to_datetime(early, level, _adjust(cnd.level, cnd.value))
    return (early, late)

def duration(rng):
    """Calculate the number of seconds contained in a by a date Range."""

    seconds = 0
    early = pendulum.create(1, 1, 1, 0, 0, 0)
    late = pendulum.create(1, 1, 1, 0, 0, 0)
    smallest_and_level = None
    for an_and in sorted(rng.ands):
        smallest_and_level = an_and.level
        (early, late) = _add_condition_to_datetimes(an_and, None, early, late)
    if len(rng.ors) == 0:
        late = add_to_datetime(late,
                               level_to_datetime_unit(smallest_and_level),
                               1)
        seconds += (late - early).total_seconds()
    else:
        for grp in rng.ors:
            erly = early.copy()
            lte = late.copy()
            for cnd in sorted(grp):
                (erly, lte) = _add_condition_to_datetimes(cnd, grp.position, erly, lte)
                if len(grp) == 1 and cnd.sign == '=':
                    lte = add_to_datetime(lte,
                                          level_to_datetime_unit(cnd.level),
                                          1)
            secs = (lte - erly).total_seconds()
            assert secs > 0, 'vaccuous condition in group ' + str(grp)
            seconds += secs
    return seconds

def add_to_datetime(dtime, unit, value):
    keywords = {unit: value}
    return dtime.add(**keywords)


def get_min(level):
    """Get the minimum value for a date unit."""
    if level == Level.YYYY:
        return 1
    elif level == Level.MM:
        return 1
    elif level == Level.DD:
        return 1
    elif level == Level.HH:
        return 0
    elif level == Level.MIN:
        return 0

def get_max(level, dtime):
    """Get the maximum value for a date unit."""
    if level == Level.YYYY:
        return 9999
    elif level == Level.MM:
        return 12
    elif level == Level.DD:
        return monthrange(dtime.date().year, dtime.date().month)[1]
    elif level == Level.HH:
        return 23
    elif level == Level.MIN:
        return 59

def at_min(level, value):
    """Determine if a value is the min value for a date unit."""
    return get_min(level) == value

def at_max(level, dtime, value):
    """Determine if a value is the max value for a date unit."""
    return get_max(level, dtime) == value

def dt_value_for_level(dtime, level):
    if level == Level.YYYY:
        return dtime.year
    elif level == Level.MM:
        return dtime.month
    elif level == Level.DD:
        return dtime.day
    elif level == Level.HH:
        return dtime.hour
    elif level == Level.MIN:
        return dtime.minute

def level_followed_by_all_mins(dtime):
    """Determine if lowest level date unit which is followed by
    date units at their minimum level.
    """
    return_level = Level.MIN  # get lowest level to make it dynamic
    for level in reversed(list(enums.Level)):
        return_level = level
        if not at_min(level, dt_value_for_level(dtime, level)):
            break
    return return_level


def datetime_to_dateparts(dtime):
    """Create a list of DatePart objects representing a datetime."""
    parts = []
    smallest_non_min = level_followed_by_all_mins(dtime)
    for level in enums.Level:
        parts.append(DatePart(level,
                              dt_value_for_level(dtime, level),
                              get_min(level),
                              get_max(level, dtime),
                              smallest_non_min <= level))
    return parts

def level_to_datetime_unit(level):
    if level == Level.YYYY:
        return 'years'
    elif level == Level.MM:
        return 'months'
    elif level == Level.DD:
        return 'days'
    elif level == Level.HH:
        return 'hours'
    elif level == Level.MIN:
        return 'minutes'

def datestr_to_dt(datestr, tzone):
    """Create a datetime object from a yyyy[mm[dd[mm[ss]]]] string."""
    error = None
    try:
        if len(datestr) == 4:
            dtime = pendulum.Pendulum.create_from_format(datestr, '%Y', tzone)
        elif len(datestr) == 6:
            dtime = pendulum.Pendulum.create_from_format(datestr, '%Y%m', tzone)
        elif len(datestr) == 8:
            dtime = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d', tzone)
        elif len(datestr) == 10:
            dtime = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d%H', tzone)
        elif len(datestr) == 12:
            dtime = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d%H%M', tzone)
        else:
            error = 'Illegal datestr format [{0}]'.format(datestr)
    except ValueError as exn:
        error = 'Couldn\'t parse datestr [{0}]: {1}'.format(datestr, exn)

    if error:
        raise ValueError(error)

    return dtime

def deltastr_to_td(deltastr):
    pattern = r'^(\d+)(days|hours|minutes)$'
    matched = re.match(pattern, deltastr)
    if not matched:
        raise ValueError('illegal slop value [{0}] Must match {1}'.format(deltastr, pattern))
    keywords = {}
    keywords[matched.group(2)] = int(matched.group(1))
    return timedelta(**keywords)

@attr.s
class DatePart(object):
    level = attr.ib(validator=attr.validators.instance_of(Level))
    value = attr.ib(validator=attr.validators.instance_of(int))
    min_value = attr.ib(validator=attr.validators.instance_of(int))
    max_value = attr.ib(validator=attr.validators.instance_of(int))
    all_mins_follow = attr.ib(validator=attr.validators.instance_of(bool))
    def __str__(self):
        return 'level={} {} all_mins_follow={}'.format(self.level, self.value, self.all_mins_follow)
    def at_min(self):
        return self.value == self.min_value
    def at_max(self):
        return self.value == self.max_value
