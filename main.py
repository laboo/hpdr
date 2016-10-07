#!/usr/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import hpdr
from string import Template
from collections import OrderedDict
from datetime import datetime
import sys
import argparse
import pendulum
import re
import tabulate


def main(args):
    kw = {}
    if args.tz: kw['tz'] = args.tz
    if args.otz: kw['otz'] = args.otz
    if args.slop: kw['slop'] = args.slop
    if args.years: kw['years'] = args.years
    if args.months: kw['months'] = args.months
    if args.days: kw['days'] = args.days
    if args.hours: kw['hours'] = args.hours
    if args.minutes: kw['minutes'] = args.minutes
    
    spec = hpdr.build(args.begin,
                      args.end,
                      **kw)
                      
    print(spec.get_partition_range().build_display(pretty=args.pretty))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='hpdr -- Hive Partition Date Range')
    parser.add_argument('-b', '--begin', required=True, help='beginning time, inclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    parser.add_argument('-e', '--end', required=True, help='end time, exclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    parser.add_argument('-s', '--slop', required=False, help='extra duration to add to end time in \d+(years|months|days|hours|minutes) format.')
    parser.add_argument('-z', '--tz', required=False, help='input time zone for begin and end times in tzdata format, e.g. Asia/Katmandu. Defaults to UTC.')
    parser.add_argument('-o', '--otz', required=False, help='output time zone for begin and end times in tzdata format, e.g. Asia/Katmandu. Defaults to UTC.')
    parser.add_argument('-p', '--pretty', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--years', required=False, default='YYYY', help='display symbols for years.')
    parser.add_argument('--months', required=False, default='MM', help='display symbols for months.')
    parser.add_argument('--days', required=False, default='DD', help='display symbols for days.')
    parser.add_argument('--hours', required=False, default='HH', help='display symbols for hours.')
    parser.add_argument('--minutes', required=False, default='MIN', help='display symbols for minutes.')
    args = parser.parse_args()
    main(args)
