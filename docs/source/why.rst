Why hpdr?
#########

Partition date ranges are hard.
*******************************

At its heart, hpdr peforms a single, seemingly simple task. It builds a Hive Query Language (HQL) time range condition out of partitions for year, month, day, etc. Something like this::

    YYYY=2016 AND MM=05

That's how you have to specify "all of May 2016" when your partitions are YYYY, MM, and DD, instead of something easier to work with, like YYYYMMDD.

Seems simple enough, but it can quickly grow out of control.
::

    (
        (YYYY=2015 AND MM=12 AND DD=28 AND HH>=18)
     OR (YYYY=2015 AND MM=12 AND DD>28)
     OR (YYYY=2016 AND MM=01 AND DD<28)
     OR (YYYY=2016 AND MM=01 AND DD=28 AND HH<18)
    )

This also represents a one month span (2015 Dec 28, 6PM - 2016 Jan 28, 6PM), but it's more complicated. And easier to get wrong. 
In order to trust date ranges, they need to be auto-generated from a human-readable format.

Timezones make them harder.
***************************

Assuming the previous date range was for America/Los_Angeles, here it is converted to UTC.
::

    (
        (YYYY=2015 AND MM=12 AND DD=29 AND HH>=02)
     OR (YYYY=2015 AND MM=12 AND DD>29)
     OR (YYYY=2016 AND MM=01 AND DD<29)
     OR (YYYY=2016 AND MM=01 AND DD=29 AND HH<02)
    )

For Asia/Calcutta, it looks like this.
::

    (
        (YYYY=2015 AND MM=12 AND DD=28 AND HH=12 AND MIN>=30)
     OR (YYYY=2015 AND MM=12 AND DD=28 AND HH>12)
     OR (YYYY=2015 AND MM=12 AND DD>28)
     OR (YYYY=2016 AND MM=01 AND DD<28)
     OR (YYYY=2016 AND MM=01 AND DD=28 AND HH<12)
     OR (YYYY=2016 AND MM=01 AND DD=28 AND HH=12 AND MIN<30)
    )

You want to reuse your work.
****************************

When you write a complex date range by hand, it takes a while to get right, and you're still not sure it is. A few months later, 
when you need to rerun your query over a new date range, you're going to have to redo all that work.

You want to save time and money.
********************************

Opting for an overly inclusive date range because it's easier to write is a waste of computing cycles and your time. As our 
data gets bigger and bigger, processing a few extra hours or days worth gets more and more expensive.

You're nice.
************

When you process more data than you need to, you're stealing resources from other people running their own jobs in the shared grid.


