The payoff
#################

Your query
*************

Suppose you have to write a (greatly simplified) query with the following requirements:

  * It runs every day
  * It gathers data over the past 5 days from a single table
  * It must accomodate dates specified the America/Los_Angeles, though the data is stored in UTC in Hive
  * It must additionally fetch data from the partitions for the 1 hour just before and after the time range the query covers
  * The *ts* column is a string data type representing unix time since the epoch in milliseconds
  
Middle of the month
*********************

Here's what your query might look like for the middle of May 2016::
  
  SET BEGIN='2016-05-15'
  SET END='2016-05-20'
  SELECT * FROM my_table WHERE 
  ts > CAST(unix_timestamp(${hiveconf:BEGIN}, 'yyyy-MM-dd') as bigint) * 1000 AND
  ts < CAST(unix_timestamp(${hiveconf:END}, 'yyyy-MM-dd') as bigint) * 1000 AND
  (YYYY=2016 AND MM=05 AND ((DD=14 AND HH>=16) OR (DD>14 AND DD<19) OR (DD=19 AND HH<18)))

At the end of the month, when you cross the May/June border, you'd have this::

  SET BEGIN='2016-05-30'
  SET END='2016-06-04'
  SELECT * FROM my_table WHERE 
  ts > CAST(unix_timestamp(${hiveconf:BEGIN}, 'yyyy-MM-dd') as bigint) * 1000 AND
  ts < CAST(unix_timestamp(${hiveconf:END}, 'yyyy-MM-dd') as bigint) * 1000 AND
  (YYYY=2016 AND ((MM=05 AND DD=29 AND HH>=16) OR (MM=05 AND DD>29) OR (MM=06 AND DD<03) OR (MM=06 AND DD=03 AND HH<18)))


Or, you can create a hpdr template. It's just a query with HPDR\_ variables in it::

  # q.hql
  SELECT * FROM my_table WHERE
  ts > ${HPDR_slop_begin_unixtime_ms} AND
  ts < ${HPDR_slop_end_unixtime_ms} AND
  ${HPDR_range}

Then use it to create your query by using a hpdr date range. For example, with the main.py example::

  > main.py -b 20160515 -e 20160520 --dzone America/Los_Angeles -s 1hours -f q.hql
  -- tmp.hql
  SELECT * FROM my_table WHERE
  ts > 1463266800000 AND
  ts < 1463706000000 AND
  (YYYY=2016 AND MM=05 AND ((DD=14 AND HH>=16) OR (DD>14 AND DD<19) OR (DD=19 AND HH<18)))

And::

  > main.py -b 20160530 -e 20160604 --dzone America/Los_Angeles -s 1hours -f q.hql
  -- tmp.hql
  SELECT * FROM my_table WHERE
  ts > 1464562800000 AND
  ts < 1465002000000 AND
  (YYYY=2016 AND ((MM=05 AND DD=29 AND HH>=16) OR (MM=05 AND DD>29) OR (MM=06 AND DD<03) OR (MM=06 AND DD=03 AND HH<18)))

You can get a list of all the HPDR\_ variables with the *-v* flag::

   > main.py -b 20160530 -e 20160604 --dzone America/Los_Angeles -s 1hours -f /tmp/q.hql -v
    -- tmp.hql
    SELECT * FROM my_table WHERE
    ts > 1464562800000 AND
    ts < 1465002000000 AND
    (YYYY=2016 AND ((MM=05 AND DD=29 AND HH>=16) OR (MM=05 AND DD>29) OR (MM=06 AND DD<03) OR (MM=06 AND DD=03 AND HH<18)))
    -----------------------------------------------------------------------
    -- Parts of this query were auto-generated with hpdr (pip install hpdr)
    --
    --  /home/mlibucha/Envs/3hpdr/bin/python ../main.py -b 20160530 -e 20160604 --dzone America/Los_Angeles -s 1hours -f /tmp/q.hql -v
    --
    --
    -- Input:
    ---------
    -- -- tmp.hql
    -- SELECT * FROM my_table WHERE
    -- ts > ${HPDR_slop_begin_unixtime_ms} AND
    -- ts < ${HPDR_slop_end_unixtime_ms} AND
    -- ${HPDR_range}
    ----------
    -- Output:
    ----------
    -- -- tmp.hql
    -- SELECT * FROM my_table WHERE
    -- ts > 1464562800000 AND
    -- ts < 1465002000000 AND
    -- (YYYY=2016 AND ((MM=05 AND DD=29 AND HH>=16) OR (MM=05 AND DD>29) OR (MM=06 AND DD<03) OR (MM=06 AND DD=03 AND HH<18)))
    ----------
    --
    -- This is a complete list of the available template variables and their values:
    --
    -- variable                     value
    -- ---------------------------  -------------------
    -- HPDR_dzone                   UTC
    -- HPDR_qzone                   America/Los_Angeles
    -- HPDR_begin_ts                2016-05-29 17:00:00
    -- HPDR_end_ts                  2016-06-03 17:00:00
    -- HPDR_slop_begin_ts           2016-05-29 16:00:00
    -- HPDR_slop_end_ts             2016-06-03 18:00:00
    -- HPDR_begin_unixtime          1464566400
    -- HPDR_begin_unixtime_ms       1464566400000
    -- HPDR_begin_yyyymmdd          20160529
    -- HPDR_begin_yyyy              2016
    -- HPDR_begin_mm                05
    -- HPDR_begin_dd                29
    -- HPDR_begin_hh                17
    -- HPDR_begin_min               00
    -- HPDR_begin_sec               00
    -- HPDR_end_unixtime            1464998400
    -- HPDR_end_unixtime_ms         1464998400000
    -- HPDR_end_yyyymmdd            20160603
    -- HPDR_end_yyyy                2016
    -- HPDR_end_mm                  06
    -- HPDR_end_dd                  03
    -- HPDR_end_hh                  17
    -- HPDR_end_min                 00
    -- HPDR_end_sec                 00
    -- HPDR_slop_begin_unixtime     1464562800
    -- HPDR_slop_begin_unixtime_ms  1464562800000
    -- HPDR_slop_begin_yyyymmdd     20160529
    -- HPDR_slop_begin_yyyy         2016
    -- HPDR_slop_begin_mm           05
    -- HPDR_slop_begin_dd           29
    -- HPDR_slop_begin_hh           16
    -- HPDR_slop_begin_min          00
    -- HPDR_slop_begin_sec          00
    -- HPDR_slop_end_unixtime       1465002000
    -- HPDR_slop_end_unixtime_ms    1465002000000
    -- HPDR_slop_end_yyyymmdd       20160603
    -- HPDR_slop_end_yyyy           2016
    -- HPDR_slop_end_mm             06
    -- HPDR_slop_end_dd             03
    -- HPDR_slop_end_hh             18
    -- HPDR_slop_end_min            00
    -- HPDR_slop_end_sec            00
    --
    -- Note that all values have been shifted to the query time zone (HPDR_qzone)
