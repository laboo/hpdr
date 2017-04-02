import pytest
import pendulum
from tests.test_all import durations_match, all

def do_100(span):
    dt_now = pendulum.now()
    dt_100 = dt_now.add(**{span: 100})
    dt_next = dt_now
    count = 0
    while dt_next < dt_100:
        dt_next = dt_next.add(**{span: 1})
        all(dt_now, dt_next)
        count += 1

def test_months():
    do_100('months')
    
def test_days():
    do_100('days')

def test_years():
    do_100('years')

