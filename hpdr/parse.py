from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
import token
import string
try:
    from io import StringIO
except ImportError:
    from io import StringIO
from tokenize import generate_tokens, NL, TokenError
from future import standard_library
from funcparserlib.parser import (some, a, many, skip, finished, maybe, NoParseError)
standard_library.install_aliases()

# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods

SIGNS = ('<', '<=', '=', '>=', '>')
UNITS = ('YYYY', 'MM', 'DD', 'HH', 'MIN')
DIGITS = [x for x in string.digits]

class Token(object):
    '''Represents a token for a lexer.'''
    def __init__(self, code, value, start=(0, 0), stop=(0, 0), line=''):
        self.code = code
        self.value = value
        self.start = start
        self.stop = stop
        self.line = line

    @property
    def type(self):
        return token.tok_name[self.code]
    def __unicode__(self):
        pos = '-'.join('%d,%d' % x for x in [self.start, self.stop])
        return "%s %s '%s'" % (pos, self.type, self.value)
    def __repr__(self):
        return 'Token(%r, %r, %r, %r, %r)' % (
            token.tok_name[self.code], self.value, self.start, self.stop, self.line)
    def __eq__(self, other):
        return (self.code, self.value) == (other.code, other.value)

def tokenize(a_string):
    '''Break a string into a list of tokens.

    Turns the string a_string into a list of Token objects
    using the Python source code tokenizer.
    str -> [Token]

    Returns:
       The list of tokens parsed out of the string.
    '''
    return list(Token(*t)
                for t in generate_tokens(StringIO(a_string).readline)
                if t[0] not in [token.NEWLINE, NL])

def parse(tokens):
    '''Parses an SQL date range.

    Parses a list of Token object to see if it's a valid SQL
    clause meeting the following conditions:
    An optional sequence of ANDed simple conditions ANDed with
    an optional sequence of ORed complex condtions.
    Where a simple condition is a date unit, a sign, and a date value.
    And a complex condition is any legal SQL combination of simple
    conditions ANDed or ORed together.
    Date unit: YYYY, MM, DD, HH, MIN
    Sign: <, <=, =, >=, >
    Date value: any integer value, with an optional leading zero

    Returns:
       True if the tokens reprsent a valid SQL date range, False otherwise.
    '''
    try:
        left_paren = some(lambda t: t.value in '(')
        right_paren = some(lambda t: t.value in ')')
        oper = some(lambda t: t.value in SIGNS)
        unit = some(lambda t: t.value in UNITS)
        padded_num = some(lambda t: t.code == 2) + some(lambda t: t.code == 2) # hmmm, better way???
        raw_num = some(lambda t: t.code == 2)
        num = padded_num | raw_num
        cond = unit + oper + num

        endmark = a(Token(token.ENDMARKER, ''))
        end = skip(endmark + finished)

        ands = maybe(cond + maybe(many(a(Token(token.NAME, 'AND')) + cond)))
        or_ands = left_paren + ands + right_paren
        ors_without_ands = or_ands + maybe(many(a(Token(token.NAME, 'OR')) + or_ands))
        ors_with_ands = (a(Token(token.NAME, 'AND')) + left_paren + or_ands +
                         maybe(many(a(Token(token.NAME, 'OR')) + or_ands)) + right_paren)
        ors = maybe(ors_without_ands | ors_with_ands)
        full = left_paren + ands + ors + right_paren + end

        full.parse(tokens)
    except NoParseError:
        return False
    except TokenError:
        return False
    return True
