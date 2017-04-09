Can you trust it?
#################

How do you know it's right?
***************************

hpdr prints out some HQL when we call it with a couple of datetime objects, but how can we be sure what it prints out is accurate?

We could pretty print it and try to reason it out, but the whole purpose of hpdr in the first place is to eliminate that kind of
tedious, error-prone approach.

Reversing the algorithm
***********************

hpdr is tested by comparing the number of seconds between the two datetime objects with the number of seconds represented by each
clause in the HQL output added together. Let's look at a simple example.

.. code-block:: python

  #!/usr/bin/python2.7

  from datetime import datetime

  begin = datetime(2016, 02, 02, 18)
  end = datetime(2016, 05, 11, 3, 56)
  print((end - begin).total_seconds())

This prints *8502960.0* (seconds).

When we have hpdr print out the range, we get::

  (
   YYYY=2016 AND
   (
       (MM=02 AND DD=02 AND HH>=18)
    OR (MM=02 AND DD>02)
    OR (MM>02 AND MM<05)
    OR (MM=05 AND DD<11)
    OR (MM=05 AND DD=11 AND HH<03)
    OR (MM=05 AND DD=11 AND HH=03 AND MIN<56)
   )
  )

We can calcuate how many seconds each clause in HQL query represents by starting at the earliest possible datetime
for the begin and end times, and then triangulating the durations each HQL condition represents.

======================== ======= ================ ================
condition group          seconds from (inclusive) to (exclusive)
======================== ======= ================ ================
MM=02 DD=02 HH>=18         21600 2016-02-02 18:00 2016-02-03 00:00
MM=02 DD>02              2332800 2016-02-03 00:00 2016-03-01 00:00
MM>02 MM<05              5270400 2016-03-01 00:00 2016-05-01 00:00
MM=05 DD<11               864000 2016-05-01 00:00 2016-05-11 00:00
MM=05 DD=11 HH<03          10800 2016-05-11 00:00 2016-05-11 03:00
MM=05 DD=11 HH=03 MIN<56    3360 2016-05-11 03:00 2016-05-11 03:56
total                    8502960
======================== ======= ================ ================

If we further prohibit any empty condition groups -- those which evaluate to 0 seconds -- we can be fairly certain
the results are correct.
