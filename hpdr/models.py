from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import zip
from builtins import int
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
from .enums import Level, Position
import copy
import attr
import pytz
from datetime import datetime, timedelta

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
        
    def _zero_padded_value(self, value):
        if len(str(value)) == 1:
            return '0' + str(value)
        else:
            return str(value)
    def __str__(self):
        return ((Condition.display[self.level] if self.level in Condition.display else self.level.name)
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
        return self.position == other.position and sorted(self.conditions) == sorted(other.conditions)
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
                    ors_str_group = ' AND '.join('{0}'.format(x) for x in sorted(ors_group.conditions))
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
                    ors_str_group = ' AND '.join('{0}'.format(x) for x in sorted(ors_group.conditions))
                    ors_str_groups.append(ors_str_group)
                    ors_str = ' OR '.join(('({0})' if len(ors) > 1 else '{0}').format(x) for x in ors_str_groups)
                if len(ors) > 1:
                    ors_str = '(' + ors_str + ')'
            if ands or len(ors) == 1:
                out = '(' + ands_str + ors_str + ')'
            else:
                out = ands_str + ors_str
            
        return out

@attr.s
class DatePart(object):
    level = attr.ib(validator=attr.validators.instance_of(Level))
    value = attr.ib(validator=attr.validators.instance_of(int))
    min_value = attr.ib(validator=attr.validators.instance_of(int))
    max_value = attr.ib(validator=attr.validators.instance_of(int))
    all_mins_follow = attr.ib(validator=attr.validators.instance_of(bool))
    def __str__(self):
        return 'level={} {} all_mins_follow={}'.format(self.level, self.value, self.all_mins_follow)
    def at_min(self):
        return self.value == self.min_value
    def at_max(self):
        return self.value == self.max_value


class Spec(object):

    def __init__(self,
                 begin,
                 end,
                 izone='UTC',
                 ozone='UTC',
                 slop=None,
                 years='YYYY',
                 months='MM',
                 days='DD',
                 hours='HH',
                 minutes='MIN'):
        from . import utils
                
        in_zone = pytz.timezone(izone)
        out_zone = pytz.timezone(ozone)
        
        self.begin = self._localize_dt(begin, in_zone, izone)
        self.end = self._localize_dt(end, in_zone, izone)
        self.slop = slop if (not slop or (type(slop) is timedelta)) else utils.deltastr_to_td(slop)
        self.slop_end = (self.end + self.slop) if self.slop else self.end
        self.partition_range = self._build_range(self.begin, self.slop_end)
        Condition.set_display(Level.YYYY, years)
        Condition.set_display(Level.MM, months)
        Condition.set_display(Level.DD, days)
        Condition.set_display(Level.HH, hours)
        Condition.set_display(Level.MIN, minutes)

    def _localize_dt(self, dt, zone, zone_str):
        from . import utils
        if type(dt) is datetime:
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                return zone.localize(dt)
            else:
                return dt
        elif type(dt) is str:
            return utils.datestr_to_dt(dt, zone_str)
        else: # This handle Pendulum datetimes which are never naive (ie, always have timezones)
            return dt

    # Could be a static method
    def _build_range(self, begin, end):
        from . import utils
        ands = []
        ors = []
        parts1 = utils.datetime_to_dateparts(begin)
        parts2 = utils.datetime_to_dateparts(end)
        finished = False
        bli = None  # bridge_level_index

        #  Build the ANDs
        for i, (p1, p2) in enumerate(zip(parts1, parts2)):
            bli = i
            if p1.value == p2.value:
                ands.append(Condition(p1.level, '=', p1.value, p1.max_value))
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
    
        return Range(ands, ors)
        
    def get_partition_range(self):
        return self.partition_range

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
    
    def substitute(self,
                   query,
                   verbose=False,
                   pretty=False):
    
        hpdr = self.partition_range.build_display(pretty=False)
        hpdr_pretty = self.partition_range.build_display(pretty=True)
        utc_begin = xxx
        utc_end = yyy
        formats_list = []
        formats_list.append(('begin_ts', self.begin.format('%Y-%m-%d %H:%M:%S')))
        formats_list.append(('end_ts', self.end.format('%Y-%m-%d %H:%M:%S')))
        formats_list.append(('slop_end_ts', self.slop_end.format('%Y-%m-%d %H:%M:%S')))
        formats_list.append(('utc_begin_ts', utc_begin.format('%Y-%m-%d %H:%M:%S')))
        formats_list.append(('utc_end_ts', utc_end.format('%Y-%m-%d %H:%M:%S')))
        formats_list += formats_for_datetime('begin', self.begin)
        formats_list += formats_for_datetime('end', self.end)
        formats_list += formats_for_datetime('utc_begin', utc_begin)
        formats_list += formats_for_datetime('utc_end', utc_end)
        formats_list += formats_for_datetime('slop_end', self.slop_end)
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
    
        
