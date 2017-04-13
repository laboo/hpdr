Advanced features
#################

Specifying slop
*******************************

The data you're after is not always in the "right" partitions. For example, you may want all data for the month of May, but due to
clock skew, or network delays, some of the data for May sits in the partition for the last hour of April or the first hour of June.
This little bit of extra "slop" on both ends of the main logical time range can make specifying the partition range
a lot harder. You can use the *slop* argument to handle it.

.. code-block:: python

  #!/usr/bin/python2.7

  from hpdr import api

  begin, end = '20160501', '20160601'
  rng = api.build(begin, end, slop='1hours').partition_range

  print rng.build_display(True)  # True gets pretty print

Prints::

  (
   YYYY=2016 AND
   (
       (MM=04 AND DD=30 AND HH>=23)
    OR (MM=05)
    OR (MM=06 AND DD=01 AND HH<01)
   )
  )

This may not seem all that useful until you consider using the hpdr steps feature, described next.

  
Using steps
***********

Suppose you want to query all the data for a full year, but that's so much data that running a single query would take too long or
hog too many resources. If the query can logically be broken down into multiple queries each covering a portion of the year,
hpdr can handle the date ranges, including slop.

Here's how we can specify the ranges for 2016 in chunks of 60 days.

.. code-block:: python

  #!/usr/bin/python2.7

  from hpdr import api

  begin, end = '2016', '2017'
  specs = api.build_with_steps(begin, end, slop='1hours', step='60days')
  for spec in specs:
    print spec.partition_range.build_display(True)  # True gets pretty print


The query printed the first 60 days looks like this::

  (
      (YYYY=2015 AND MM=12 AND DD=31 AND HH>=23)
   OR (YYYY=2016 AND MM<03)
   OR (YYYY=2016 AND MM=03 AND DD=01 AND HH<01)
  )

And for the second, like this::
     
  (
   YYYY=2016 AND
   (
       (MM=02 AND DD=29 AND HH>=23)
    OR (MM=03)
    OR (MM=04 AND DD<30)
    OR (MM=04 AND DD=30 AND HH<01)
   )
  )
  
And so on.

But even that's not that useful without templating with HPDR\_ variables.

