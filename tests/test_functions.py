from __future__ import print_function
import pytest

from hpdr import api

def build_range_with_zones():
    return api.build('201706171338', '20171010', qzone='Asia/Calcutta', dzone='America/New_York')

def test_simple():
    rng = build_range_with_zones()
    query = 'select ${HPDR_from_time(ts)} FROM my_table'
    assert(rng.substitute(query) ==
           "select FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts, 'America/New_York'), 'Asia/Calcutta') FROM my_table")

def test_multiple_replacements():
    rng = build_range_with_zones()
    query = 'select ${HPDR_from_time(ts)}, ${HPDR_from_time(ts2)} FROM my_table'
    assert(rng.substitute(query) ==
           "select FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts, 'America/New_York'), 'Asia/Calcutta'), FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts2, 'America/New_York'), 'Asia/Calcutta') FROM my_table")

def test_multiple_line():
    rng = build_range_with_zones()
    query = '''
select
${HPDR_from_time(ts)},
${HPDR_from_time(ts2)}
FROM my_table
    '''
    response = '''
select
FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts, 'America/New_York'), 'Asia/Calcutta'),
FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts2, 'America/New_York'), 'Asia/Calcutta')
FROM my_table
    '''
    assert(rng.substitute(query) == response)

def test_no_tz():
    rng = api.build('201706171338', '20171010')
    query = 'select ${HPDR_from_time(ts)} FROM my_table'
    assert(rng.substitute(query) == "select FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts, 'UTC'), 'UTC') FROM my_table")

def test_just_dzone():
    rng = api.build('201706171338', '20171010', dzone='America/Denver')
    query = 'select ${HPDR_from_time(ts)} FROM my_table'
    assert(rng.substitute(query) == "select FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts, 'America/Denver'), 'UTC') FROM my_table")

def test_just_qzone():
    rng = api.build('201706171338', '20171010', qzone='America/Denver')
    query = 'select ${HPDR_from_time(ts)} FROM my_table'
    assert(rng.substitute(query) == "select FROM_UTC_TIMESTAMP(TO_UTC_TIMESTAMP(ts, 'UTC'), 'America/Denver') FROM my_table")
    
