try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from tokenize import generate_tokens, NL
import operator, token
from funcparserlib.parser import (some, a, oneplus, many, skip,
                                  finished, maybe, with_forward_decls,
                                  NoParseError)
import string

SIGNS = ('<', '<=', '=', '>=', '>')
UNITS = ('YYYY', 'MM', 'DD', 'HH', 'MIN')
DIGITS = [x for x in string.digits]
#DIGITS = oneplus(some(lambda c: c.isdigit()))
class Token(object):
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

def tokenize(s):
    'str -> [Token]'
    return list(Token(*t)
                for t in generate_tokens(StringIO(s).readline)
                if t[0] not in [token.NEWLINE, NL])

def parse(tokens):
    try:
        for t in tokens:
            #print(t)
            pass
        left_paren = some(lambda t: t.value in ('('))
        right_paren = some(lambda t: t.value in (')'))
        op = some(lambda t: t.value in SIGNS)
        unit = some(lambda t: t.value in UNITS)
        padded_num = some(lambda t: t.code == 2) + some(lambda t: t.code == 2) # hmmm, better way???
        raw_num = some(lambda t: t.code == 2)
        num = padded_num | raw_num
        cond = unit + op + num

        endmark = a(Token(token.ENDMARKER, ''))
        end = skip(endmark + finished)

        ands = maybe(cond + maybe(many(a(Token(token.NAME,'AND')) + cond)))
        or_ands = left_paren + ands + right_paren
        ors_without_ands = or_ands + maybe(many(a(Token(token.NAME,'OR')) + or_ands))
        ors_with_ands = a(Token(token.NAME,'AND')) + left_paren + or_ands + maybe(many(a(Token(token.NAME,'OR')) + or_ands)) + right_paren
        ors = maybe(ors_without_ands | ors_with_ands)
        # ors = maybe(a(Token(token.NAME,'AND')) + left_paren + or_ands + maybe(many(a(Token(token.NAME,'OR')) + or_ands) + right_paren))
        full = left_paren + ands + ors + right_paren + end
        
        full.parse(tokens)
    except NoParseError as npe:
        print(npe)
        return False
    return True
        
#print(parse(tokenize("(MM>15)")))
#print(parse(tokenize("(MM>15 AND HH=3)")))
#print(parse(tokenize("(MM>15 AND DD=3 AND MIN=1 )")))
#print(parse(tokenize("(MM>15 AND DD=3 AND MIN=1 AND ((HH=04 AND MM=4) OR (MM=1 AND HH=5) OR (MM=2)))")))
#print(parse(tokenize("(YYYY=2018 AND MM=12 AND ((DD=2 AND HH=3 AND MIN>=4) OR (DD=2 AND HH>3) OR (DD>2 AND DD<5)))")))
#print(parse(tokenize("MM>15 (AND)")))

