#!/usr/bin/env python3.5

import copy
import attr
from .enums import Level, Position

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
class ConditionsGroup():
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
class Clause(object):
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
    

