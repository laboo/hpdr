import argparse

def parse_args(args):
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
    PARSER.add_argument('-z', '--tz', required=False,
                        help=('input time zone for begin and end times in tzdata format, '
                              'e.g. Asia/Katmandu. Defaults to UTC.'))
    PARSER.add_argument('-q', '--qtz', required=False,
                        help=('query time zone for begin and end times in tzdata format, '
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
    return PARSER.parse_args()
