import re

def from_time(args, qzone, dzone):
    args_array = args.split(',')
    if len(args_array) != 1:
        raise Exception("'HPDR_from_time' function requires 1 argument")
    
    out = ''
    date = args_array[0]
    try:
        int_date = int(date)
        # If this looks like seconds, covert it to milliseconds
        if int_date <= 9999999999:
            int_date *= 1000
            out = "FROM_UTC_TIMESTAMP(" + str(int_date) + ", '" + qzone + "')"
    except ValueError:
        utc = "TO_UTC_TIMESTAMP(" + date + ", '" + dzone + "')"
        out = "FROM_UTC_TIMESTAMP(" + utc + ", '" + qzone + "')"
    return out

FUNCTIONS = {'from_time': from_time}
REGEX = re.compile('\${HPDR_(.*?)\((.*?)\)}')

def replace_all(line, qzone, dzone):
    replacements = []
    for match in re.finditer(REGEX, line):
        name = match.group(1)
        if name not in FUNCTIONS:
            raise Exception('Unsupported method: ', name)
        args = match.group(2)
        replacements.append((match, FUNCTIONS[name](args, qzone, dzone)))

    new_line = ''
    start = 0
    for r in replacements:
        m = r[0]  # match
        t = r[1]  # text
        new_line += line[start:m.start()] + t
        start = m.end()
    new_line += line[start:]
    return new_line


if __name__ == '__main__':
    line = "select ${HPDR_from_time(1497033144)}, ${HPDR_from_time('2017-06-09 07:32:24')} from somewhere"
    qzone = 'America/Los_Angeles'
    dzone = 'America/New_York'
    print(line)
    print(replace_all(line, qzone, dzone))
