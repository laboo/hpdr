Examples
########

main.py
*******

`<https://github.com/laboo/hpdr/blob/master/main.py>`_

This simple script exposes all the functionality in hpdr. Here are a few examples::


  > ./main.py -b 20160312 -e 20160412
    (YYYY=2016 AND ((MM=03 AND DD>=12) OR (MM=04 AND DD<12)))

With a timezone::
      
  > ./main.py -b 20160312 -e 20160412 -q America/Los_Angeles -p
    (
    YYYY=2016 AND
     (
          (MM=03 AND DD=12 AND HH>=08)
      OR (MM=03 AND DD>12)
      OR (MM=04 AND DD<12)
      OR (MM=04 AND DD=12 AND HH<07)
     )
    )

The arguments::
      
  >  ./main.py -h
  usage: main.py [-h] -b BEGIN -e END [-t STEP] [-s SLOP] [-l LSLOP] [-r RSLOP]
                 [-d DZONE] [-q--qzone Q__QZONE] [-p] [-v] [-f FILE]
                 [--years YEARS] [--months MONTHS] [--days DAYS] [--hours HOURS]
                 [--minutes MINUTES]
 
steps.py
********

`<https://github.com/laboo/hpdr/blob/master/steps.py>`_

This script requires input and output file arguments. It substitutes range values the HPDR\_ variables in the
input query file and writes the result to the output file in steps.
