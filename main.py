#!/usr/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from hpdr import api
import argparse


def main(args):
    kw = {}
    if args.tz: kw['izone'] = args.tz
    if args.qtz: kw['qzone'] = args.qtz
    if args.slop: kw['slop'] = args.slop
    if args.years: kw['years'] = args.years
    if args.months: kw['months'] = args.months
    if args.days: kw['days'] = args.days
    if args.hours: kw['hours'] = args.hours
    if args.minutes: kw['minutes'] = args.minutes
    
    spec = api.build(args.begin,
                     args.end,
                     **kw)

    if args.file:
        query = open(args.file, 'r').read()
        print(spec.substitute(query, args.verbose, args.pretty))
    else:
        print(spec.get_partition_range().build_display(pretty=args.pretty))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='hpdr -- Hive Partition Date Range')
    parser.add_argument('-b', '--begin', required=True, help='beginning time, inclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    parser.add_argument('-e', '--end', required=True, help='end time, exclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    parser.add_argument('-s', '--slop', required=False, help='extra duration to add to end time in \d+(years|months|days|hours|minutes) format.')
    parser.add_argument('-z', '--tz', required=False, help='input time zone for begin and end times in tzdata format, e.g. Asia/Katmandu. Defaults to UTC.')
    parser.add_argument('-q', '--qtz', required=False, help='query time zone for begin and end times in tzdata format, e.g. Asia/Katmandu. Defaults to UTC.')
    parser.add_argument('-p', '--pretty', action='store_true', help='pretty print output. Not relevant if --file option specified.')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-f', '--file', help="File to perform substitution on.")
    parser.add_argument('--years', required=False, default='YYYY', help='display symbols for years.')
    parser.add_argument('--months', required=False, default='MM', help='display symbols for months.')
    parser.add_argument('--days', required=False, default='DD', help='display symbols for days.')
    parser.add_argument('--hours', required=False, default='HH', help='display symbols for hours.')
    parser.add_argument('--minutes', required=False, default='MIN', help='display symbols for minutes.')
    args = parser.parse_args()
    main(args)
