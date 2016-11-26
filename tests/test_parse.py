from __future__ import print_function
from __future__ import unicode_literals
import pytest

from hpdr import parse as p

def p_and_t(cond):
    try:
        rv = p.parse(p.tokenize(cond))
    except:
        rv = False
    return rv

def test_empty():
    assert p_and_t('()')
    
def test_simple_cond():
    assert p_and_t('(MM>15)')
    
def test_and_cond():
    assert p_and_t('(MM>15 AND HH=3)')

def test_double_and_cond():
    assert p_and_t('(MM>15 AND DD=3 AND MIN=1 )')

def test_complex_cond():
    assert p_and_t('(MM>15 AND DD=3 AND MIN=1 AND ((HH=04 AND MM=4) OR (MM=1 AND HH=5) OR (MM=2)))')

def test_large_cond():
    assert p_and_t('(YYYY=2018 AND MM=12 AND ((DD=2 AND HH=3 AND MIN>=4) OR (DD=2 AND HH>3) OR (DD>2 AND DD<5)))')

def test_ors_only():
    assert not p_and_t('((DD=2 AND HH=3 AND MIN>=4) OR (DD=2 AND HH>3) OR (DD>2 AND DD<5)))')
    
def test_bad_simple():
    assert not p_and_t('MM>15 (AND)')
    
def test_bad_unmatched():
    assert not p_and_t('(')

def test_bad_unmatched2():
    assert not p_and_t('(MM=10) AND (HH>2))')

