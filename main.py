#!/usr/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
import argparse
from future import standard_library
from hpdr import api
standard_library.install_aliases()

def main(args):
    keywords = {}
    if args.step: keywords['step'] = args.step
    if args.tz: keywords['szone'] = args.stz
    if args.qtz: keywords['dzone'] = args.dtz
    if args.slop: keywords['slop'] = args.slop
    if args.lslop: keywords['lslop'] = args.lslop
    if args.rslop: keywords['rslop'] = args.rslop
    if args.years: keywords['years'] = args.years
    if args.months: keywords['months'] = args.months
    if args.days: keywords['days'] = args.days
    if args.hours: keywords['hours'] = args.hours
    if args.minutes: keywords['minutes'] = args.minutes

    specs = api.build_with_steps(args.begin,
                                 args.end,
                                 **keywords)

    for spec in specs:
        if args.file:
            query = open(args.file, 'r').read()
            print(spec.substitute(query, args.verbose, args.pretty))
        else:
            print(spec.partition_range.build_display(pretty=args.pretty))

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='hpdr -- Hive Partition Date Range')
    PARSER.add_argument('-b', '--begin', required=True,
                        help='beginning time, inclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    PARSER.add_argument('-e', '--end', required=True,
                        help='end time, exclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    PARSER.add_argument('-t', '--step', required=False,
                        help=('return multiple Spec objects broken down into duration in '
                              '\\d+(days|hours|minutes) format.'))
    PARSER.add_argument('-s', '--slop', required=False,
                        help=('extra duration to add to both ends of range in '
                              '\\d+(days|hours|minutes) format.'))
    PARSER.add_argument('-l', '--lslop', required=False,
                        help=('extra duration to add to beginning of range in '
                              '\\d+(days|hours|minutes) format.'))
    PARSER.add_argument('-r', '--rslop', required=False,
                        help=('extra duration to add to end of range in '
                              '\\d+(days|hours|minutes) format.'))
    PARSER.add_argument('--stz', required=False,
                        help=('timezone data is stored in, in tzdata format, '
                              'e.g. Asia/Katmandu. Defaults to UTC.'))
    PARSER.add_argument('--dtz', required=False,
                        help=('timezone range is displayed in, in tzdata format, '
                              'e.g. Asia/Katmandu. Defaults to UTC.'))
    PARSER.add_argument('-p', '--pretty', action='store_true',
                        help='pretty print output. Not relevant if --file option specified.')
    PARSER.add_argument('-v', '--verbose', action='store_true')
    PARSER.add_argument('-f', '--file',
                        help="File to perform substitution on.")
    PARSER.add_argument('--years', required=False, default='YYYY',
                        help='display symbols for years.')
    PARSER.add_argument('--months', required=False, default='MM',
                        help='display symbols for months.')
    PARSER.add_argument('--days', required=False, default='DD',
                        help='display symbols for days.')
    PARSER.add_argument('--hours', required=False, default='HH',
                        help='display symbols for hours.')
    PARSER.add_argument('--minutes', required=False, default='MIN',
                        help='display symbols for minutes.')
    ARGS = PARSER.parse_args()
    main(ARGS)
