#!/usr/bin/env python

import subprocess, os, os.path, tempfile, datetime, argparse, sys
from hpdr import api

def main(args):

    begin = datetime.datetime(2017, 1, 1)
    end = datetime.datetime(2017, 2, 1)

    with open(args.file) as query_file:
        template = query_file.read()
        specs = api.build_with_steps(begin=args.begin,
                                     end=args.end,
                                     step=args.step,
                                     slop=args.slop,
                                     lslop=args.lslop,
                                     rslop=args.rslop,
                                     szone=args.stz,
                                     dzone=args.dtz,
                                     years=args.years,
                                     months=args.months,
                                     days=args.days,
                                     hours=args.hours,
                                     minutes=args.minutes)
        if os.path.isfile(args.out):
            os.remove(args.out)

        for i, spec in enumerate(specs):
            query = spec.substitute(template)
            if i == 0:
                query = 'set hive.cli.print.header=true;\n' + query
            print('query=', query)
            with tempfile.NamedTemporaryFile() as f:
                if sys.version_info[0] < 3:
                    f.write(query)
                else:
                    f.write(bytes(query, "UTF-8"))
                f.flush()
                cmd = ['/usr/bin/hive', '-f',  f.name]
                #print(spec.partition_range.build_display())
                #print(spec.variables_map['HPDR_begin_ts'])
                #print('*' * 10 + spec.get_partition_range().build_display())
                with open(args.out, 'a') as outfile:
                    #subprocess.check_call(cmd, stdout=outfile)
                    pass
                
if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='steps.py -- hpdr query in steps')
    PARSER.add_argument('-b', '--begin', required=True,
                        help='beginning time, inclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    PARSER.add_argument('-e', '--end', required=True,
                        help='end time, exclusive, in YYYY[[MM][[DD][HH][NN]]] format.')
    PARSER.add_argument('-f', '--file', required=True,
                        help="File to perform substitution on.")
    PARSER.add_argument('-o', '--out', required=True,
                        help="Output file.")
    PARSER.add_argument('-t', '--step', required=True,
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
