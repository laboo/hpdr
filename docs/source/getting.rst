Getting started
###############

Installation
*******************************

hpdr has been tested Python 2.7, and Python 3.5 and 3.6. It won't work with 2.6.

Install it with pip::
  
 pip install hpdr

Simple API Usage
*******************************

Two dates are required. They can be Python datetime objects, subclasses of datetime, or strings.

.. code-block:: python

  #!/usr/bin/python2.7

  from datetime import datetime
  from hpdr import api

  begin, end = datetime(2016, 12, 1), '20170203'
  rng = api.build(begin, end).partition_range

  print rng.build_display(True)  # True gets pretty print

Prints::
    
  (
      (YYYY=2016 AND MM>=12)
   OR (YYYY=2017 AND MM<02)
   OR (YYYY=2017 AND MM=02 AND DD<03)
  )

With timezones
*******************************

The datetime objects passed as the *begin* and *end* arguments must NOT have timezones associated with them, The timezone
is assumed to be UTC unless you pass a different timezone with the *dzone* argument. The *dzone* timezone specifies
the timezone the data is **stored** in, in Hive.

To specify the timezone the data is used in the **query**, use the *qzone* argument. If you don't specify *qzone*,
UTC is used.

.. code-block:: python

  #!/usr/bin/python2.7

  from datetime import datetime
  from hpdr import api

  begin, end = datetime(2016, 12, 1), '20170203'
  rng = api.build(begin, end,
                  dzone='America/Los_Angeles',
                  qzone='Asia/Calcutta',
                 ).partition_range

  print rng.build_display(True)  # True gets pretty print

Prints::

  (
      (YYYY=2016 AND MM=12 AND DD=01 AND HH=13 AND MIN>=30)
   OR (YYYY=2016 AND MM=12 AND DD=01 AND HH>13)
   OR (YYYY=2016 AND MM=12 AND DD>01)
   OR (YYYY=2017 AND MM<02)
   OR (YYYY=2017 AND MM=02 AND DD<03)
   OR (YYYY=2017 AND MM=02 AND DD=03 AND HH<13)
   OR (YYYY=2017 AND MM=02 AND DD=03 AND HH=13 AND MIN<30)
  )

With your partition names
*******************************

If your partition names are not *YYYY*, *MM*, *DD*, etc., which are the defaults for hpdr, you can pass your own names.

.. code-block:: python

   #!/usr/bin/python2.7

   from hpdr import api
   
   begin, end = '20161201', '20170215'
   rng = api.build(begin, end, years='YEAR', months='MONTH', days='DAY').partition_range
   
   print rng.build_display(True)
   
Prints::
  
  (
   (    YEAR=2016 AND MONTH>=12)
    OR (YEAR=2017 AND MONTH<02)
    OR (YEAR=2017 AND MONTH=02 AND DAY<15)
   )
  )

