# pylint: disable=redefined-builtin, too-few-public-methods, no-member,too-many-branches
# pylint: disable=too-many-arguments, too-many-locals
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import zip
from builtins import int
from builtins import str
from builtins import object
from datetime import datetime, timedelta
from string import Template
from collections import OrderedDict
import copy
import sys
import attr
import tabulate
import pendulum
from future import standard_library
from six import string_types
from .enums import Level, Position
from . import utils
standard_library.install_aliases()

@attr.s(cmp=False)
class Condition(object):
    display = {}  # class level attribute
    level = attr.ib(validator=attr.validators.instance_of(Level))
    sign = attr.ib()
    value = attr.ib(validator=attr.validators.instance_of(int))
    max_value = attr.ib(validator=attr.validators.instance_of(int))

    @staticmethod
    def set_display(level, value):
        Condition.display[level] = value

    @staticmethod
    def _zero_padded_value(value):
        if len(str(value)) == 1:
            return '0' + str(value)
        else:
            return str(value)

    def __str__(self):
        return ((Condition.display[self.level]
                 if self.level in Condition.display else self.level.name)
                + self.sign
                + self._zero_padded_value(self.value))
    def __eq__(self, other):
        return self.level == other.level and int(self.value) == int(other.value)
    def __ne__(self, other):
        return self != other
    def __lt__(self, other):
        return (self.level < other.level or
                (self.level == other.level and int(self.value) < int(other.value)))
    def __le__(self, other):
        return (self < other) or (self == other)
    def __gt__(self, other):
        return (self.level > other.level or
                (self.level == other.level and int(self.value) > int(other.value)))
    def __ge__(self, other):
        return (self > other) or (self == other)

@attr.s(cmp=False)
class ConditionsGroup(object):
    position = attr.ib(validator=attr.validators.instance_of(Position))
    conditions = attr.ib(init=False, default=attr.Factory(list))

    def add(self, condition):
        self.conditions.append(condition)
    def pop(self):
        return self.conditions.pop()
    def __str__(self):
        if self.conditions:
            return str(self.position) + ' ' + ' '.join([str(x) for x in sorted(self.conditions)])
        else:
            return ''
    #def __str__(self):
    #    return self.__repr__()
    def __iter__(self):
        return self.conditions.__iter__()
    def __getitem__(self, key):
        return self.conditions.__getitem__(key)
    def __len__(self):
        return len(self.conditions)
    def __eq__(self, other):
        return (self.position == other.position and
                sorted(self.conditions) == sorted(other.conditions))
    def __ne__(self, other):
        return self != other
    def __lt__(self, other):
        if self.position < other.position:
            return True
        if self.position == other.position:
            if self.position == Position.left:
                if len(self.conditions) > len(other.conditions):
                    return True
            elif self.position == Position.right:
                if len(self.conditions) < len(other.conditions):
                    return True
    def __le__(self, other):
        return (self < other) or (self == other)
    def __gt__(self, other):
        if self.position > other.position:
            return True
        if self.position == other.position:
            if self.position == Position.left:
                if len(self.conditions) < len(other.conditions):
                    return True
            elif self.position == Position.right:
                if len(self.conditions) > len(other.conditions):
                    return True
    def __ge__(self, other):
        return (self > other) or (self == other)

@attr.s
class Range(object):
    ands = attr.ib(validator=attr.validators.instance_of(list))  # list of Condition
    ors = attr.ib(validator=attr.validators.instance_of(list))   # list of ConditionsGroup

    def build_display(self, pretty=False):
        ands_str = ''
        ors_str = ''
        out = ''
        # Use copies because we might manipulate them, and manipulating might
        # break duration testing
        ors = copy.deepcopy(self.ors)
        ands = copy.deepcopy(self.ands)
        if (len(ors) == 1 and
                len(ors[0].conditions) == 1 and
                ors[0].conditions[0].sign == '='):
            the_only_group = ors.pop()
            the_only_condition = the_only_group.conditions.pop()
            ands.append(the_only_condition)
        if pretty:
            out += '(\n'

            if ands:
                out += ' AND '.join('{0}'.format(x) for x in ands)
            if ors:
                ors_str_groups = []
                if ands:
                    out += ' AND\n (\n'
                for ors_group in sorted(ors):
                    ors_str_group = ' AND '.join('{0}'.format(x)
                                                 for x in sorted(ors_group.conditions))
                    ors_str_groups.append(ors_str_group)
                for i, group in enumerate(ors_str_groups):
                    if i == 0:
                        out += '     (' + group + ')' + '\n'
                    else:
                        out += '  OR (' + group + ')' + '\n'
                if ands:
                    out += " )" + '\n'
            if not out.endswith('\n'):
                out += '\n'
            out += ')'
        else:
            if ands:
                ands_str += ' AND '.join('{0}'.format(x) for x in ands)
            if ors:
                ors_str_groups = []
                if ands:
                    ands_str += (' AND ')
                for ors_group in sorted(ors):
                    ors_str_group = ' AND '.join('{0}'.format(x)
                                                 for x in sorted(ors_group.conditions))
                    ors_str_groups.append(ors_str_group)
                    ors_str = ' OR '.join(('({0})' if len(ors) > 1 else '{0}').format(x)
                                          for x in ors_str_groups)
                if len(ors) > 1:
                    ors_str = '(' + ors_str + ')'
            if ands or len(ors) == 1:
                out = '(' + ands_str + ors_str + ')'
            else:
                out = ands_str + ors_str
        return out

class Spec(object):
    def __init__(self,
                 begin,
                 end,
                 izone='UTC',
                 qzone='UTC',
                 slop=None,
                 lslop=None,
                 rslop=None,
                 years='YYYY',
                 months='MM',
                 days='DD',
                 hours='HH',
                 minutes='MIN'):
        self.izone = izone
        self.qzone = qzone
        self.begin = Spec._shift_dt(begin, izone, qzone)
        self.end = Spec._shift_dt(end, izone, qzone)
        self._build_slop(slop, lslop, rslop)
        self.partition_range = Spec._build_range(self.begin, self.slop_end)
        Condition.set_display(Level.YYYY, years)
        Condition.set_display(Level.MM, months)
        Condition.set_display(Level.DD, days)
        Condition.set_display(Level.HH, hours)
        Condition.set_display(Level.MIN, minutes)

    @staticmethod
    def _not_a_delta_str(slop):
        return not slop or (isinstance(slop, timedelta))

    @staticmethod
    def _calc_slop(slop):
        return slop if Spec._not_a_delta_str(slop) else utils.deltastr_to_td(slop)

    def _build_slop(self, slop, lslop, rslop):
        add_to_begin = Spec._calc_slop(lslop) if lslop else Spec._calc_slop(slop)
        add_to_end = Spec._calc_slop(rslop) if rslop else Spec._calc_slop(slop)
        self.slop_begin = (self.begin - add_to_begin) if add_to_begin else self.begin
        self.slop_end = (self.end + add_to_end) if add_to_end else self.end

    @staticmethod
    def _shift_dt(dtime, i_zone_str, q_zone_str):
        if isinstance(dtime, pendulum.pendulum.Pendulum):
            pass  # pendulum types are good
        elif isinstance(dtime, datetime):
            if dtime.tzinfo is not None:
                raise ValueError('Only naive datetime.datetimes allowed, don''t set tzinfo')
            dtime = pendulum.create(dtime.year,
                                    dtime.month,
                                    dtime.day,
                                    dtime.hour,
                                    dtime.minute,
                                    dtime.second,
                                    dtime.microsecond,
                                    i_zone_str if i_zone_str else 'UTC')
        elif isinstance(dtime, string_types):
            dtime = utils.datestr_to_dt(dtime, i_zone_str)
        else:
            raise ValueError('Unrecognized datetime type: ' + type(dtime))
        return dtime.in_timezone(q_zone_str if q_zone_str else 'UTC')

    @staticmethod
    def _build_range(begin, end):
        ands = []
        ors = []
        parts1 = utils.datetime_to_dateparts(begin)
        parts2 = utils.datetime_to_dateparts(end)
        finished = False
        bli = None  # bridge_level_index

        #  Build the ANDs
        for i, (part1, part2) in enumerate(zip(parts1, parts2)):
            bli = i
            if part1.value == part2.value:
                ands.append(Condition(part1.level, '=', part2.value, part1.max_value))
            else:
                break

        if finished:
            return Range(ands, ors)

        # Build the ORs
        # First the bridge, if there is one
        if bli is not None:
            if (parts2[bli].value - parts1[bli].value) > 1:
                bridge = ConditionsGroup(Position.middle)
                left_sign = '>=' if parts1[bli].all_mins_follow else '>'
                bridge.add(Condition(parts1[bli].level, left_sign,
                                     parts1[bli].value, parts1[bli].max_value))
                bridge.add(Condition(parts2[bli].level, '<',
                                     parts2[bli].value, parts2[bli].max_value))
                ors.append(bridge)
            elif (parts2[bli].value - parts1[bli].value) == 1 and parts1[bli].all_mins_follow:
                bridge = ConditionsGroup(Position.middle)
                bridge.add(Condition(parts1[bli].level, '=',
                                     parts1[bli].value, parts1[bli].max_value))
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
            grp = ConditionsGroup(Position.left)
            for j, part1 in enumerate(reversed(parts1[:i])):
                sign = '>' if j == 0 else '='
                if part1.all_mins_follow:
                    if part1.at_min():
                        # continue  # we don't want >=0
                        break
                    sign = '>='
                if sign == '>' and part1.at_max():  # vaccuous
                    grp.conditions = []  # wipe out this entire group
                    break
                grp.add(Condition(part1.level, sign, part1.value, part1.max_value))
            if grp.conditions:
                ors.append(grp)

        # Finally the ors that come after the bridge
        for i in range(2, len(parts2) + 1, 1):
            grp = ConditionsGroup(Position.right)
            for j, part2 in enumerate(reversed(parts2[:i])):
                sign = '<' if j == 0 else '='
                if part2.all_mins_follow or sign == '<':
                    if part2.at_min():
                        # continue  # we don't want <=0
                        break
                grp.add(Condition(part2.level, sign, part2.value, part2.max_value))
            if grp.conditions:
                ors.append(grp)

        return Range(ands, ors)

    def get_partition_range(self):
        return self.partition_range

    @staticmethod
    def formats_for_datetime(prefix, dtime):
        formats = []
        formats.append((prefix + '_unixtime', dtime.strftime('%s')))
        formats.append((prefix + '_unixtime_ms', dtime.strftime('%s000')))
        formats.append((prefix + '_yyyymmdd', dtime.format('%Y%m%d')))
        formats.append((prefix + '_yyyy', dtime.format('%Y')))
        formats.append((prefix + '_mm', dtime.format('%m')))
        formats.append((prefix + '_dd', dtime.format('%d')))
        formats.append((prefix + '_hh', dtime.format('%H')))
        formats.append((prefix + '_min', dtime.format('%M')))
        formats.append((prefix + '_sec', dtime.format('%S')))
        return formats

    @staticmethod
    def comment_out(text):
        out = ''
        for line in text.split('\n'):
            out += '-- ' + line + '\n'
        return out

    def substitute(self,
                   query,
                   verbose=False,
                   pretty=False):
        timestamp_pattern = '%Y-%m-%d %H:%M:%S'
        hpdr_prefix = 'HPDR_'
        hpdr = self.partition_range.build_display(pretty=False)
        hpdr_pretty = self.partition_range.build_display(pretty=True)
        formats_list = []
        formats_list.append((hpdr_prefix + 'izone', self.izone))
        formats_list.append((hpdr_prefix + 'qzone', self.qzone))
        formats_list.append((hpdr_prefix + 'begin_ts', self.begin.format(timestamp_pattern)))
        formats_list.append((hpdr_prefix + 'end_ts', self.end.format(timestamp_pattern)))
        formats_list.append((hpdr_prefix + 'slop_begin_ts',
                             self.slop_begin.format(timestamp_pattern)))
        formats_list.append((hpdr_prefix + 'slop_end_ts', self.slop_end.format(timestamp_pattern)))        
        formats_list += Spec.formats_for_datetime(hpdr_prefix + 'begin', self.begin)
        formats_list += Spec.formats_for_datetime(hpdr_prefix + 'end', self.end)
        formats_list += Spec.formats_for_datetime(hpdr_prefix + 'slop_begin', self.slop_begin)
        formats_list += Spec.formats_for_datetime(hpdr_prefix + 'slop_end', self.slop_end)
        formats = OrderedDict(formats_list)

        # Build this table first, when it doesn't have $hpdr in it yet, cause it doesn't print well
        # with $hpdr in it
        table_with_comments = ''
        if verbose:
            table = tabulate.tabulate([(x, y) for x, y in formats.items()],
                                      headers=['variable', 'value'])
            for row in table.split('\n'):
                table_with_comments += '-- ' + row + '\n'
        formats[hpdr_prefix + 'range'] = hpdr
        formats[hpdr_prefix + 'range_pretty'] = hpdr_pretty
        if query:
            template_input = query
        else:
            template_input = hpdr_pretty if pretty else hpdr
        template = Template(template_input)
        filled = template.substitute(formats)
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
                out += Spec.comment_out(template_input)
                out += '----------\n'
                out += '-- Output:\n'
                out += '----------\n'
                out += Spec.comment_out(filled)
                out += '----------\n'
            out += '--\n'
            out += ('-- This is a complete list of the available '
                    'template variables and their values:\n')
            out += '--\n'
            out += table_with_comments
            out += '--\n'            
            out += '-- Note that all values have been shifted to the query time zone (HPDR_qzone)\n'            
        return out
