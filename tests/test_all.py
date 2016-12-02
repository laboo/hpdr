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

def durations_match(c, dt1, dt2):
    calc = utils.duration(c)
    real = (dt2 - dt1).total_seconds()
    assert real == calc, 'real duration ({}) != calculated duration ({})'.format(real, calc)

def all(dt1, dt2):
    rng = api.build(dt1, dt2).get_partition_range()
    p = rng.build_display(pretty=True)
    d = rng.build_display(pretty=False)
    print(d)
    print(p)
    durations_match(rng, dt1, dt2)
    assert parse.parse(parse.tokenize(p))
    assert parse.parse(parse.tokenize(d))

def test_demo_hour():
    all(pendulum.create(2016,9,9,22,8,0,0),
        pendulum.create(2016,9,9,23,22,0,0))
def test_demo_day():
    all(pendulum.create(2016,9,9,23,8,0,0),
        pendulum.create(2016,9,10,0,22,0,0))
def test_demo_month():
    all(pendulum.create(2016,8,9,23,8,0,0),
        pendulum.create(2016,9,10,0,22,0,0))
def test_demo_year():
    all(pendulum.create(2016,8,9,23,8,0,0),
        pendulum.create(2017,9,10,0,22,0,0))

def test_now():
    all(pendulum.create(2014,1,4,23,19,0,0),
        pendulum.create(2015,2,3,0,1,0,0))

def test_one_minute():
    all(pendulum.create(2014,1,1,0,0,0,0),
        pendulum.create(2014,1,1,0,1,0,0))

def test_one_hour():
    all(pendulum.create(2014,1,1,0,0,0,0),
        pendulum.create(2014,1,1,1,0,0,0))
    
def test_demo2():
    all(datetime(2016,12,31,23,58),
        datetime(2017,1,1,0,2))

def test_full_year():
    all(datetime(2017,1,1),
        datetime(2018,1,1))

def test_full_month():
    all(datetime(2017,1,1),
        datetime(2017,2,1))

def test_full_day():
    all(datetime(2017,1,1),
        datetime(2017,1,2))

def test_full_hour():
    all(datetime(2017,1,1,0),
        datetime(2017,1,1,1))
    
def test_full_minute():
    all(datetime(2017,1,1,0,0),
        datetime(2017,1,1,0,1))
    
def test_0():
    all(datetime(2018,8,31),
        datetime(2018,9,7))

def test_10():
    all(datetime(2018,1,1),
        datetime(2018,1,2))
    
def test_1():
    all(datetime(2018,12,2),
        datetime(2018,12,3,5))

def test_2():
    all(datetime(2018,12,2,3,4),
        datetime(2018,12,5))

def test_3():
    all(datetime(2018,12,2),
        datetime(2018,12,5))

def test_4():
    all(datetime(2017,12,6, 2, 2),
       datetime(2018,12,2, 8, 23))

def test_5():
    all(datetime(2014,12,6, 2, 2),
        datetime(2018,12,2, 8, 23))
    
def test_min_month():
    all(pendulum.create(2014,1,1,0,0,0,0),
        pendulum.create(2014,2,2,0,0,0,0))

def test_min_day():
    all(pendulum.create(2014,3,1,0,0,0,0),
        pendulum.create(2014,3,2,0,0,0,0))

