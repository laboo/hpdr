from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import pytest
import pendulum
from datetime import datetime
from hpdr import parse, utils, api
from random import randint

def durations_match(one_spec, specs):
    many = 0
    for spec in specs:
        rng = spec.get_partition_range()
        many += utils.duration(rng)
    one_rng = one_spec.get_partition_range()
    one = utils.duration(one_rng)
    #print('\nmany duration ({}) one duration ({})'.format(many, one))
    assert many == one, 'many duration ({}) != one duration ({})'.format(many, one)


def compare(begin, end, slop=None, lslop=None, rslop=None, step=None):
    one = api.build(begin, end,
                    slop=slop,
                    lslop=lslop,
                    rslop=rslop)
    many = api.build_with_steps(begin, end,
                                slop=slop,
                                lslop=lslop,
                                rslop=rslop,
                                step=step)
    durations_match(one, many)
    
def test1():
    compare('20160901',
            '20161001',
            slop='2hours',
            step='1days')

def test2():
    compare('20160901',
            '20161001',
            slop='2hours',
            step='5days')

def test3():
    compare('20160901',
            '20161001',
            lslop='1days',
            step='3days')

def test4():
    compare('20160901',
            '20161001',
            lslop='10days',
            step='60days') # larger than duration
   
    

