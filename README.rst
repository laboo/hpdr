HPDR: Hive Partition Date Ranges
================================

When your Hive partitions are YYYY, MM, DD, HH and not YYYYMMDDHH, composing date
ranges with them can get out of control. hpdr solves this problem.

.. code-block:: python

    >>> from hpdr import api
    >>> rng = api.build('2016102612', '2017122612').get_partition_range()
    >>> print(rng.build_display())
    ((YYYY=2016 AND MM=10 AND DD=26 AND HH>=12) OR (YYYY=2016 AND MM=10 AND DD>26)
    OR (YYYY=2016 AND MM>10) OR (YYYY=2017 AND MM<12) OR (YYYY=2017 AND MM=12 AND DD<26)
    OR (YYYY=2017 AND MM=12 AND DD=26 AND HH<12))
    >>> print(rng.build_display(pretty=True))
    (
         (YYYY=2016 AND MM=10 AND DD=26 AND HH>=12)
      OR (YYYY=2016 AND MM=10 AND DD>26)
      OR (YYYY=2016 AND MM>10)
      OR (YYYY=2017 AND MM<12)
      OR (YYYY=2017 AND MM=12 AND DD<26)
      OR (YYYY=2017 AND MM=12 AND DD=26 AND HH<12)
    )

Maybe you think in local time but store your data in UTC?

.. code-block:: python

    >>> from hpdr import api
    >>> rng = api.build('2016102612', '2017122612',
    ...                 izone='America/Los_Angeles',
    ...                 qzone='UTC').get_partition_range()
    >>> print(rng.build_display(pretty=True))
    (
         (YYYY=2016 AND MM=10 AND DD=26 AND HH>=19)
      OR (YYYY=2016 AND MM=10 AND DD>26)
      OR (YYYY=2016 AND MM>10)
      OR (YYYY=2017 AND MM<12)
      OR (YYYY=2017 AND MM=12 AND DD<26)
      OR (YYYY=2017 AND MM=12 AND DD=26 AND HH<20)

Or maybe your date range is too large to run in one query, and it's a pain to break it down?

.. code-block:: python

    import subprocess, os, os.path, tempfile, datetime
    from hpdr import api
    
    QUERY_FILE = 'myquery.hql'
    OUT_FILE = 'out.txt'
    begin = datetime.datetime(2016, 11, 1)
    end = datetime.datetime(2016, 11, 30)
    step = '5days'
    
    with open(QUERY_FILE) as f:
        template = f.read()
    
    specs = api.build_with_steps(begin=begin, end=end, step=step)
    
    if os.path.isfile(OUT_FILE):
        os.remove(OUT_FILE)
    
    for spec in specs:
        query = spec.substitute(template)
        with tempfile.NamedTemporaryFile() as f:
            f.write(query)
            f.flush()
            cmd = ['/usr/bin/hive', '-f',  f.name]
            print(spec.get_partition_range().build_display())
            with open(OUT_FILE, 'a') as outfile:
                subprocess.check_call(cmd, stdout=outfile)

This prints::

    (YYYY=2016 AND MM=11 AND DD>=01 AND DD<06)
    (YYYY=2016 AND MM=11 AND DD>=06 AND DD<11)
    (YYYY=2016 AND MM=11 AND DD>=11 AND DD<16)
    (YYYY=2016 AND MM=11 AND DD>=16 AND DD<21)
    (YYYY=2016 AND MM=11 AND DD>=21 AND DD<26)
    (YYYY=2016 AND MM=11 AND DD>=26 AND DD<30)

It runs 6 Hive queries built from a template containing HPDR\_ variables. Something like this:

::

    SELECT
      YEAR(event_timestamp),
      MONTH(event_timestamp),
      DAY(event_timestamp),
      FROM my_table
      WHERE
        event_timestamp >= '${HPDR_begin_ts}'
        event_timestamp < '${HPDR_end_ts}'
        AND ${HPDR_range}

The first query looks like this.

::

    SELECT
      YEAR(event_timestamp),
      MONTH(event_timestamp),
      DAY(event_timestamp),
      FROM my_table
      WHERE
        event_timestamp >= '2016-11-01 00:00:00'
        event_timestamp < '2016-11-06 00:00:00'

The full list of HPDR\_ variables available for that first query is::

    variable                     value
    ---------------------------  -------------------
    HPDR_izone                   UTC
    HPDR_qzone                   UTC
    HPDR_begin_ts                2016-11-01 00:00:00
    HPDR_end_ts                  2016-11-06 00:00:00
    HPDR_slop_begin_ts           2016-11-01 00:00:00
    HPDR_slop_end_ts             2016-11-06 00:00:00
    HPDR_begin_unixtime          1477983600
    HPDR_begin_unixtime_ms       1477983600000
    HPDR_begin_yyyymmdd          20161101
    HPDR_begin_yyyy              2016
    HPDR_begin_mm                11
    HPDR_begin_dd                01
    HPDR_begin_hh                00
    HPDR_begin_min               00
    HPDR_begin_sec               00
    HPDR_end_unixtime            1478415600
    HPDR_end_unixtime_ms         1478415600000
    HPDR_end_yyyymmdd            20161106
    HPDR_end_yyyy                2016
    HPDR_end_mm                  11
    HPDR_end_dd                  06
    HPDR_end_hh                  00
    HPDR_end_min                 00
    HPDR_end_sec                 00
    HPDR_slop_begin_unixtime     1477983600
    HPDR_slop_begin_unixtime_ms  1477983600000
    HPDR_slop_begin_yyyymmdd     20161101
    HPDR_slop_begin_yyyy         2016
    HPDR_slop_begin_mm           11
    HPDR_slop_begin_dd           01
    HPDR_slop_begin_hh           00
    HPDR_slop_begin_min          00
    HPDR_slop_begin_sec          00
    HPDR_slop_end_unixtime       1478415600
    HPDR_slop_end_unixtime_ms    1478415600000
    HPDR_slop_end_yyyymmdd       20161106
    HPDR_slop_end_yyyy           2016
    HPDR_slop_end_mm             11
    HPDR_slop_end_dd             06
    HPDR_slop_end_hh             00
    HPDR_slop_end_min            00
    HPDR_slop_end_sec            00
