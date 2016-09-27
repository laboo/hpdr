#!/usr/bin/env python3.5

import utils.datetime_utils as dtu
from utils.enums import Level, Position
from utils.classes import Condition, ConditionsGroup, Clause, DatePart
from string import Template
from collections import OrderedDict
import sys
import argparse
import pendulum
import re
import tabulate


def die(msg):
    print(msg)
    sys.exit()
    
def datestr_to_dt(datestr):
    error = None
    try:
        if len(datestr) == 4:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y')
        elif len(datestr) == 6:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m')
        elif len(datestr) == 8:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d')
        elif len(datestr) == 10:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d%H')
        elif len(datestr) == 12:
            dt = pendulum.Pendulum.create_from_format(datestr, '%Y%m%d%H%M')
        else:
            error = 'Illegal datestr format [{0}]'.format(datestr)
    except Exception as e:
        error = 'Couldn\'t parse datestr [{0}]: {1}'.format(datestr, e)

    if error:
        die(error)

    return dt

def main(args):
    Condition.set_display(Level.YYYY, args.years)
    Condition.set_display(Level.MM, args.months)
    Condition.set_display(Level.DD, args.days)
    Condition.set_display(Level.HH, args.hours)
    Condition.set_display(Level.MIN, args.minutes)
    
    utc_begin_dt = datestr_to_dt(args.begin)
    utc_end_dt = datestr_to_dt(args.end)

    if args.tz:
        try:
            begin_dt = utc_begin_dt.in_tz(args.tz)
            end_dt = utc_end_dt.in_tz(args.tz)
        except Exception as e:
            die(e)
    else:
        begin_dt = utc_begin_dt
        end_dt = utc_end_dt
        
    if args.slop:
        matched = re.match(r'^(\d+)(years|months|days|hours|minutes)$', args.slop)
        if not matched:
            die('illegal slop value [{0}]'.format(args.slop))
        slop_end_dt = dtu.add_to_datetime(end_dt, matched.group(2), int(matched.group(1)))
    else:
        slop_end_dt = end_dt
        
    if begin_dt >= end_dt:
        die('begin datetime [{0} must be less than end datetime [{1}]'.format(args.begin, args.end))
    clause = build_range(begin_dt, slop_end_dt)

    query = None
    if args.filename:
        query = ''
        with open(args.filename) as f:
            for line in f:
                query += line

    hpdr = clause.build_display(pretty=False)
    hpdr_pretty = clause.build_display(pretty=True)
    print(substitute(query,
                     hpdr,
                     hpdr_pretty,
                     begin_dt,
                     end_dt,
                     slop_end_dt,
                     utc_begin_dt,
                     utc_end_dt,
                     args.verbose,
                     args.pretty))


def formats_for_datetime(prefix, dt):
    formats = []
    formats.append((prefix + '_unixtime', dt.strftime('%s')))
    formats.append((prefix + '_yyyy', dt.format('%Y')))
    formats.append((prefix + '_mm', dt.format('%m')))
    formats.append((prefix + '_dd', dt.format('%d')))
    formats.append((prefix + '_hh', dt.format('%H')))
    formats.append((prefix + '_min', dt.format('%M')))
    formats.append((prefix + '_sec', dt.format('%S')))
    return formats

def comment_out(text):
    out = ''
    for line in text.split('\n'):
        out += '-- ' + line + '\n'
    return out

def substitute(query,
               hpdr,
               hpdr_pretty,
               begin,
               end,
               slop_end,
               utc_begin,
               utc_end,
               verbose,
               pretty):
    formats_list = []
    formats_list.append(('begin_ts', begin.format('%Y-%m-%d %H:%M:%S')))
    formats_list.append(('end_ts', end.format('%Y-%m-%d %H:%M:%S')))
    formats_list.append(('slop_end_ts', slop_end.format('%Y-%m-%d %H:%M:%S')))
    formats_list.append(('utc_begin_ts', utc_begin.format('%Y-%m-%d %H:%M:%S')))
    formats_list.append(('utc_end_ts', utc_end.format('%Y-%m-%d %H:%M:%S')))
    formats_list += formats_for_datetime('begin', begin)
    formats_list += formats_for_datetime('end', end)
    formats_list += formats_for_datetime('utc_begin', utc_begin)
    formats_list += formats_for_datetime('utc_end', utc_end)
    formats_list += formats_for_datetime('slop_end', slop_end)
    formats = OrderedDict(formats_list)

    # Build this table first, when it doesn't have $hpdr in it yet, cause it doesn't print well
    # with $hpdr in it
    table_with_comments = ''
    if verbose:
        table  = tabulate.tabulate([(x,y) for x,y in formats.items()], headers=['variable', 'value'])
        for row in table.split('\n'):
            table_with_comments += '-- ' + row + '\n'
    formats['hpdr'] = hpdr
    formats['hpdr_pretty'] = hpdr_pretty
    if query:
        template = query
    else:
        template = hpdr_pretty if pretty else hpdr
    s = Template(template)
    filled = s.substitute(formats)
    out = filled
    if verbose:
        out += '\n'
        out += '-----------------------------------------------------------------------\n'
        out += '-- Parts of this query were auto-generated with hpdr (pip install hpdr)\n'
        out += '--\n'
        out += '--  ' + sys.executable + ' ' + ' '.join(sys.argv) + '\n'
        out += '--\n'
        if query:
            out += '--\n'
            out += '-- Input:\n'
            out += '---------\n'
            out += comment_out(template)
            out += '----------\n'
            out += '-- Output:\n'
            out += '----------\n'
            out += comment_out(filled)
            out += '----------\n'
        out += '--\n'
        out += '-- This is a complete list of the available template variables and their values:\n'
        out += '--\n'
        out += table_with_comments

    return out
    

    
def build_range(dt1, dt2):
    ands = []
    ors = []
    parts1 = dtu.datetime_to_dateparts(dt1)
    parts2 = dtu.datetime_to_dateparts(dt2)
    finished = False
    bli = None  # bridge_level_index

    #  Build the ANDs
    for i, (p1, p2) in enumerate(zip(parts1, parts2)):
        bli = i
        if p1.value == p2.value:
            ands.append(Condition(p1.level, '=', p1.value, p1.max_value))
            #bli = i
        # This looks pretty but it breaks testing with durations    
        #elif p1.all_mins_follow and p2.all_mins_follow:
            # we can finish this off will all ands
            #finished = True
            #if p1.value == p2.value - 1:
                # Checking for this type of case:
                # dt1=20160201 dt2=20160301 (all of, and only, February 2016)
                # which should be
                # (YYYY=2016 AND MM=02)
                # and not something like
                # (YYYY=2016 and (MM>=02 and MM<03))
                #ands.append(Condition(p1.level, '=', p1.value, p1.max_value))
            #else:
                #ands.append(Condition(p1.level, '>=', p1.value, p1.max_value))
                #ands.append(Condition(p2.level, '<', p2.value, p2.max_value))
            #break
        else:
            #bli = i
            break

    if finished:
        return Clause(ands, ors)
    
    # Build the ORs
    # First the bridge, if there is one
    if bli is not None:
        if (parts2[bli].value - parts1[bli].value) > 1:
            bridge = ConditionsGroup(Position.middle)
            left_sign = '>=' if parts1[bli].all_mins_follow else '>'
            bridge.add(Condition(parts1[bli].level, left_sign, parts1[bli].value, parts1[bli].max_value))
            bridge.add(Condition(parts2[bli].level, '<', parts2[bli].value, parts2[bli].max_value))
            ors.append(bridge)
        elif (parts2[bli].value - parts1[bli].value) == 1 and p1.all_mins_follow:
            bridge = ConditionsGroup(Position.middle)
            bridge.add(Condition(parts1[bli].level, '=', parts1[bli].value, parts1[bli].max_value))
            ors.append(bridge)
            
    # Reset the date parts because we no longer have to deal with the
    # parts that went into the ands list
    parts1 = parts1[bli:]
    parts2 = parts2[bli:]

    # Next, the ors before the bridge
    # If we've got MMDDHHCC left, the loop will show us:
    # MMDDCC, which should be MM=a AND DD=b and CC>c
    # MMDD, which should be MM=1 AND DD>b
    for i in range(len(parts1), 1, -1):
        g = ConditionsGroup(Position.left)
        for j, p1 in enumerate(reversed(parts1[:i])):
            sign = '>' if j == 0 else '='
            if p1.all_mins_follow:
                if p1.at_min():
                    # continue  # we don't want >=0
                    break
                sign = '>='
            if sign == '>' and p1.at_max():  # vaccuous
                g.conditions = []  # wipe out this entire group
                break
            g.add(Condition(p1.level, sign, p1.value, p1.max_value))
        if g.conditions:
            ors.append(g)

    # Finally the ors that come after the bridge
    for i in range(2, len(parts2) + 1, 1):
        g = ConditionsGroup(Position.right)
        for j, p2 in enumerate(reversed(parts2[:i])):
            sign = '<' if j == 0 else '='
            if p2.all_mins_follow or sign == '<':
                if p2.at_min():
                    # continue  # we don't want <=0
                    break
            g.add(Condition(p2.level, sign, p2.value, p2.max_value))
        if g.conditions:
            ors.append(g)
    
    return Clause(ands, ors)

if __name__ == '__main__':
    #main(sys.argv)
    parser = argparse.ArgumentParser(description='hpdr -- Hive Partition Date Range')
    parser.add_argument('-b', '--begin', required=True, help='beginning time, inclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    parser.add_argument('-e', '--end', required=True, help='end time, exclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    parser.add_argument('-s', '--slop', required=False, help='extra duration to add to end time in \d+(years|months|days|hours|minutes) format.')
    parser.add_argument('-z', '--tz', required=False, help='time zone for begin and end times in tzdata format, e.g. Asia/Katmandu. Defaults to UTC.')
    parser.add_argument('-f', '--filename', required=False, help='name of file containing a query with substitution placeholders. If specified, this file, with placeholders filled in is echoed to the screen instead of the default partition range.')
    parser.add_argument('-p', '--pretty', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--years', required=False, default='YYYY', help='display symbols for years.')
    parser.add_argument('--months', required=False, default='MM', help='display symbols for months.')
    parser.add_argument('--days', required=False, default='DD', help='display symbols for days.')
    parser.add_argument('--hours', required=False, default='HH', help='display symbols for hours.')
    parser.add_argument('--minutes', required=False, default='MIN', help='display symbols for minutes.')
    args = parser.parse_args()
    main(args)
