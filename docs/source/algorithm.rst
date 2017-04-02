The algorithm
#############

Details
*******

Every date range breaks down in the same way. Here's an example range
::

    ----: YYYY-MM-DD HH:MM
    From: 2017-02-15 12:30
    To  : 2017-02-25 04:00

Parsing from left to right, the first part of the range is what's common between the two datetimes: `2017-02`.
In the query these common parts are ANDed together using equals signs.
::

    YYYY=2017 AND MM=02

The first unit to differ between the two datetimes is DD, with values `15` and `25`. This is referred to in the
code as the "bridge". The bridge shows up in the query like this.
::

    (DD>15 AND DD<25)

The other two parts of the query are the entrance to, and exit from, the bridge. Our bridge excludes
the two days on the ends, the 15\ :sup:`th` and the 25\ :sup:`th`. So the entrance and exit parts must handle them.
Here's the entrance.
::

    (DD=15 AND HH=12 AND MIN>=30) OR (DD=15 AND HH>12)

And the exit.
::

    (DD=25 AND HH<04)

All together, it looks like this.
::

    (
    YYYY=2017 AND MM=02 AND             -- [shared]
     (
         (DD=15 AND HH=12 AND MIN>=30)  -- [entrance]
      OR (DD=15 AND HH>12)              -- [entrance]
      OR (DD>15 AND DD<25)              -- [bridge]
      OR (DD=25 AND HH<04)              -- [exit]
     )
    )

Requirements
************

Each date ranges hpdr outputs must be

* **Correct.**  It represent the date range precisely in compilable HQL.
* **Readable.** It must display the range in human-readable formats.
* **Minimal.**  It must be written in the fewest number of characters possible.

Correctness is a necessary condition for hpdr to be worth anything at all, but others are not.

Pretty printing helps hpdr users check the output visually, so they can verify its output.

The *minimal* requirement deserves a section of its own.

Minimal
*******

Common sense minimal
====================

There's an infinite number of bad ways to create any given date range. For example, the first 10 days of May 2015 could be written
::

    YYYY=2015 AND MM=5 AND (DD=1 OR DD=2 OR DD=3 OR DD=4 OR DD=5 OR DD=6 OR DD=7 OR DD=8 OR DD=9 OR DD=10)

But this is better
::

    YYYY=2015 AND MM=5 AND DD<11

because it's minimal.

Exceptional minimal
===================

This should be avoided.
::

    MM>=6 AND MM<7

because this is clearly better,
::

    MM=6

even though the former mirrors the base case.
::

    MM>=6 AND MM<10

Non-overlapping minimal
=======================    

A hpdr date range can be correct, but can contain overlapping conditions. A stupid example is
::

    YYYY=2016 OR (YYYY>=2010 AND YYYY <2017)  -- 2016 included twice

This is non-minimal and not allowed in hpdr. A suprising number of these were ferreted out by unit tests.

Minimal vs. readable
********************

Consider this example from above a little more closely.
::

    MM>=6 AND MM<10

It's readable, but not quite minimal. It could be written with one less character.
::

    MM>5 AND MM<10

But I consistently go with the non-minimal former option because it best represents the fact that date ranges are inclusive
at the beginning and exclusive at the end.


Questionable 
************

I wrote hpdr to scratch an itch at work. I was composing, and was watching other people composing, these massively complex Hive
date ranges. Strings turned into milliseconds truncated to seconds turned into Unix timestamps wrapped in timezone-shifting functions.
They were unreadable and unmaintainable. I thought I would whip up a nice Python module that would fix it all.

But it turned out to be much harder than I thought. The code I've written to build a date range is pretty dense. The line of 
attack I settled on is indirect. But it was the best I could come up with. 

Is there a simpler, recursive algorithm? I didn't see it.

