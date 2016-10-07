from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import int
from builtins import str
from future import standard_library
standard_library.install_aliases()
from . import enums
from .enums import Level, Position
from .models import DatePart
from calendar import monthrange
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pendulum
import re

ZERO_BASED = {Level.HH, Level.MIN}

def adjust(level, value):
    adjusted = value if level in ZERO_BASED else value - 1
    return adjusted

def add_condition_to_datetimes(c, p, early, late):
    level = level_to_datetime_unit(c.level)
    if c.sign == '=':
        early = add_to_datetime(early, level, adjust(c.level, c.value))
        late = add_to_datetime(late, level, adjust(c.level, c.value))
    elif p == Position.left:
        if c.sign == '>':
            early = add_to_datetime(early, level, adjust(c.level, c.value) + 1)
        elif c.sign == '>=':
            early = add_to_datetime(early, level, adjust(c.level, c.value))
        late = add_to_datetime(late, level, adjust(c.level, get_max(c.level, late) + 1))
    elif p == Position.right:
        early = add_to_datetime(early, level, adjust(c.level, get_min(c.level)))
        if c.sign == '<':
            late = add_to_datetime(late, level, adjust(c.level, c.value))
        elif c.sign == '<=':
            late = add_to_datetime(late, level, adjust(c.level, c.value) + 1)
    elif p == Position.middle:
        if c.sign == '<':
            late = add_to_datetime(late, level, adjust(c.level, c.value))
        elif c.sign == '>':
            early = add_to_datetime(early, level, adjust(c.level, c.value) + 1)
        elif c.sign == '>=':
            early = add_to_datetime(early, level, adjust(c.level, c.value))
    return (early,late)

def duration(r):
    seconds = 0
    early = pendulum.create(1,1,1,0,0,0)
    late = pendulum.create(1,1,1,0,0,0)
    smallest_and_level = None
    for an_and in sorted(r.ands):
        smallest_and_level = an_and.level
        (early, late) = add_condition_to_datetimes(an_and, None, early, late)
    if len(r.ors) == 0:
        late = add_to_datetime(late,
                                   level_to_datetime_unit(smallest_and_level),
                                   1)
        seconds += (late - early).total_seconds()
    else:
        for g in r.ors:
            e = early.copy()
            l = late.copy()
            for c in sorted(g):
                (e, l) = add_condition_to_datetimes(c, g.position, e, l)
                if len(g) == 1 and c.sign == '=':
                    l = add_to_datetime(l,
                                        level_to_datetime_unit(c.level),
                                        1)
            secs = (l - e).total_seconds()
            assert secs > 0, 'vaccuous condition in group ' + str(g)
            seconds += secs
    return seconds

def add_to_datetime(dt, unit, value):
    kw = {unit: value}
    return dt.add(**kw)


def get_min(level):
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

def get_max(level, dt):
    if level == Level.YYYY:
        return 9999
    elif level == Level.MM:
        return 12
    elif level == Level.DD:
        return monthrange(dt.date().year, dt.date().month)[1]
    elif level == Level.HH:
        return 23
    elif level == Level.MIN:
        return 59

def at_min(level, value):
    return get_min(level) == value

def at_max(level, dt, value):
    return get_max(level, dt) == value

def dt_value_for_level(dt, level):
    if level == Level.YYYY:
        return dt.year
    elif level == Level.MM:
        return dt.month
    elif level == Level.DD:
        return dt.day
    elif level == Level.HH:
        return dt.hour
    elif level == Level.MIN:
        return dt.minute
    
def level_followed_by_all_mins(dt):
    return_level = Level.MIN  # TODO get lowest level
    for level in reversed(enums.Level):
        return_level = level
        if not at_min(level, dt_value_for_level(dt, level)):
            break
    return return_level

def datetime_to_dateparts(dt):
    parts = []
    smallest_non_min = level_followed_by_all_mins(dt)
    for level in enums.Level:
        parts.append(DatePart(level,
                              dt_value_for_level(dt, level),
                              get_min(level),
                              get_max(level,dt),
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
    
def datestr_to_dt(datestr, tz):
    error = None
    try:
        if len(datestr) == 4:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y', tz)
        elif len(datestr) == 6:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m', tz)
        elif len(datestr) == 8:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d', tz)
        elif len(datestr) == 10:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d%H', tz)
        elif len(datestr) == 12:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d%H%M', tz)
        else:
            error = 'Illegal datestr format [{0}]'.format(datestr)
    except Exception as e:
        error = 'Couldn\'t parse datestr [{0}]: {1}'.format(datestr, e)

    if error:
        raise ValueError(error)

    return dt

def deltastr_to_td(ds):
    matched = re.match(r'^(\d+)(years|months|days|hours|minutes)$', ds)
    if not matched:
        raise ValueError('illegal slop value [{0}]'.format(ds))
    kw = {}
    kw[matched.group(2)] = int(matched.group(1))
    return timedelta(**kw)

