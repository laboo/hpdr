# pylint: disable=redefined-builtin, too-few-public-methods, no-member,too-many-branches
# pylint: disable=too-many-arguments, too-many-locals, too-many-instance-attributes
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
from hpdr.enums import Level, Position
from hpdr.utils import (Condition, ConditionsGroup,
                        deltastr_to_td, datetime_to_dateparts, datestr_to_dt)
standard_library.install_aliases()


@attr.s
class Range(object):
    '''A date range, abstractly represented by SQL conditions.'''

    _ands = attr.ib(validator=attr.validators.instance_of(list))  # list of Condition
    _ors = attr.ib(validator=attr.validators.instance_of(list))   # list of ConditionsGroup

    def build_display(self, pretty=False):
        '''Build a string for displaying the Range.

        Create a string version of the Range in valid SQL syntax for a conditional clause.
        '''

        ands_str = ''
        ors_str = ''
        out = ''
        # Use copies because we might manipulate them, and manipulating might
        # break duration testing
        ors = copy.deepcopy(self._ors)
        ands = copy.deepcopy(self._ands)
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
    """Object for representing a partition date range."""
    def __init__(self,
                 begin,
                 end,
                 dzone='UTC',
                 qzone='UTC',
                 slop=None,
                 lslop=None,
                 rslop=None,
                 years='YYYY',
                 months='MM',
                 days='DD',
                 hours='HH',
                 minutes='MIN'):
        self.dzone = dzone
        self.qzone = qzone
        self.begin = Spec._shift_dt(begin, dzone, qzone)
        self.end = Spec._shift_dt(end, dzone, qzone)
        self._build_slop(slop, lslop, rslop)
        self.partition_range = Spec._build_range(self.slop_begin, self.slop_end)
        self.partition_range_no_slop = Spec._build_range(self.begin, self.end)
        self.variables_map = self._build_variables_map()
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
        return slop if Spec._not_a_delta_str(slop) else deltastr_to_td(slop)

    def variables(self):
        '''Return a map of all HPDR\_ variables and their values defined for the range.'''
        return this.variables_map

    def _build_slop(self, slop, lslop, rslop):
        add_to_begin = Spec._calc_slop(lslop) if lslop else Spec._calc_slop(slop)
        add_to_end = Spec._calc_slop(rslop) if rslop else Spec._calc_slop(slop)
        self.slop_begin = (self.begin - add_to_begin) if add_to_begin else self.begin
        self.slop_end = (self.end + add_to_end) if add_to_end else self.end

    @staticmethod
    def _shift_dt(dtime, d_zone_str, q_zone_str):
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
                                    d_zone_str if d_zone_str else 'UTC')
        elif isinstance(dtime, string_types):
            dtime = datestr_to_dt(dtime, d_zone_str)
        else:
            raise ValueError('Unrecognized datetime type: ' + type(dtime))
        return dtime.in_timezone(q_zone_str if q_zone_str else 'UTC')

    @staticmethod
    def _build_range(begin, end):
        """Builds a Range object representing time from begin to end."""

        ands = []
        ors = []
        parts1 = datetime_to_dateparts(begin)
        parts2 = datetime_to_dateparts(end)
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
                if (parts2[bli].value - parts1[bli].value) == 2 and not parts1[bli].all_mins_follow:
                    # Prefer MM=11 to (MM>10 AND MM<12)
                    bridge.add(Condition(parts1[bli].level, '=',
                                         parts1[bli].value + 1, parts1[bli].max_value))
                else:
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

    def _build_variables_map(self):
        """Creates a map of HPDR_ variables to their values for use in
        templated hive queries.

        For example, for the date range 200312 to 200412:
          HPDR_begin_ts => '2003-12-01 00:00:00'
          HPDR_slop_begin_unixtime => '1070265600'
          HPDR_range => ((YYYY=2003 AND MM>=12) OR (YYYY>2003 AND YYYY<2014) OR (YYYY=2014 AND MM<12))
        """
        timestamp_pattern = '%Y-%m-%d %H:%M:%S'
        hpdr_prefix = 'HPDR_'
        hpdr = self.partition_range.build_display(pretty=False)
        hpdr_pretty = self.partition_range.build_display(pretty=True)
        vars_list = []
        vars_list.append((hpdr_prefix + 'dzone', self.dzone))
        vars_list.append((hpdr_prefix + 'qzone', self.qzone))
        vars_list.append((hpdr_prefix + 'begin_ts', self.begin.format(timestamp_pattern)))
        vars_list.append((hpdr_prefix + 'end_ts', self.end.format(timestamp_pattern)))
        vars_list.append((hpdr_prefix + 'slop_begin_ts',
                          self.slop_begin.format(timestamp_pattern)))
        vars_list.append((hpdr_prefix + 'slop_end_ts', self.slop_end.format(timestamp_pattern)))
        vars_list += Spec._vars_for_datetime(hpdr_prefix + 'begin', self.begin)
        vars_list += Spec._vars_for_datetime(hpdr_prefix + 'end', self.end)
        vars_list += Spec._vars_for_datetime(hpdr_prefix + 'slop_begin', self.slop_begin)
        vars_list += Spec._vars_for_datetime(hpdr_prefix + 'slop_end', self.slop_end)
        vars = OrderedDict(vars_list)
        vars[hpdr_prefix + 'range'] = hpdr
        vars[hpdr_prefix + 'range_pretty'] = hpdr_pretty
        return vars

    @staticmethod
    def _vars_for_datetime(prefix, dtime):
        vars = []
        vars.append((prefix + '_unixtime', dtime.strftime('%s')))
        vars.append((prefix + '_unixtime_ms', dtime.strftime('%s000')))
        vars.append((prefix + '_yyyymmdd', dtime.format('%Y%m%d')))
        vars.append((prefix + '_yyyy', dtime.format('%Y')))
        vars.append((prefix + '_mm', dtime.format('%m')))
        vars.append((prefix + '_dd', dtime.format('%d')))
        vars.append((prefix + '_hh', dtime.format('%H')))
        vars.append((prefix + '_min', dtime.format('%M')))
        vars.append((prefix + '_sec', dtime.format('%S')))
        return vars

    @staticmethod
    def _comment_out(text):
        out = ''
        for line in text.split('\n'):
            out += '-- ' + line + '\n'
        return out

    def substitute(self,
                   query,
                   verbose=False,
                   pretty=False):
        '''Fills in the HPDR\_ varibles with the values.

        Args:
            query (string): a string (optionally) containing HPDR\_ variables
            verbose (bool): if True prints out lots of extra info as an SQL comment
            pretty(bool): if True returns just HPDR_range_pretty variable

        Returns:
           str: query with HDPR\_ variables substituted for, or HPDR_range_pretty
           value if pretty=True
        '''

        hpdr = self.partition_range.build_display(pretty=False)
        hpdr_pretty = self.partition_range.build_display(pretty=True)

        # Build this table first, when it doesn't have $hpdr in it yet, cause it doesn't print well
        # with $hpdr in it
        table_with_comments = ''
        if verbose:
            table = tabulate.tabulate([(x, y)
                                       for x, y in self.variables_map.items()
                                       if 'range' not in x],
                                      headers=['variable', 'value'])
            for row in table.split('\n'):
                table_with_comments += '-- ' + row + '\n'
        if query:
            template_input = query
        else:
            template_input = hpdr_pretty if pretty else hpdr
        template = Template(template_input)
        filled = template.safe_substitute(self.variables_map)
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
                out += Spec._comment_out(template_input)
                out += '----------\n'
                out += '-- Output:\n'
                out += '----------\n'
                out += Spec._comment_out(filled)
                out += '----------\n'
            out += '--\n'
            out += ('-- This is a complete list of the available '
                    'template variables and their values:\n')
            out += '--\n'
            out += table_with_comments
            out += '--\n'
            out += '-- Note that all values have been shifted to the query time zone (HPDR_qzone)\n'
        return out
