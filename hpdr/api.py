# pylint: disable=too-many-arguments

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from hpdr.models import Spec
from hpdr import utils
from datetime import timedelta
standard_library.install_aliases()

        
def build(begin,
          end,
          szone='UTC',
          dzone='UTC',
          slop=None,
          lslop=None,
          rslop=None,
          years='YYYY',
          months='MM',
          days='DD',
          hours='HH',
          minutes='MIN'):
    """Build a specification for a date range.

    Args:
        begin (str/datetime): begin date of range, a datetime or yyyy[mm[dd[mm[ss]]]] string
        end (str/datetime): end date of range, a datetime or yyyy[mm[dd[mm[ss]]]] string
        szone (str): tzdata timezone data is stored in
        dzone (str): tzdata timezone range is displayed in
        slop (str): duration to add to both ends of the partition range,
            specified as \\d+[years|months|days|hours|minutes],
            for example, 5hours
        lslop (str): duration to add to the front end of the partition range,
            specified as \\d+[years|months|days|hours|minutes],
            for example, 5hours
        rslop (str): duration to add to the back end of the partition range,
            specified as \\d+[years|months|days|hours|minutes],
            for example, 5hours
        years (str): name for years partition
        months (str): name for months partition
        days (str): name for days partition
        hours (str): name for hours partition
        minutes (str): name for hours partition

    Returns: 
       hpdr.models.Spec: Object representing the date range

    """

    specs = build_with_steps(begin,
                             end,
                             szone=szone,
                             dzone=dzone,
                             slop=slop,
                             lslop=lslop,
                             rslop=rslop,
                             years=years,
                             months=months,
                             days=days,
                             hours=hours,
                             minutes=minutes)

    return specs[0]


def build_with_steps(begin,
                     end,
                     step=None,
                     szone='UTC',
                     dzone='UTC',
                     slop=None,
                     lslop=None,
                     rslop=None,
                     years='YYYY',
                     months='MM',
                     days='DD',
                     hours='HH',
                     minutes='MIN'):
    """Build a lists of specification for a date.

    The specifications in the list are contiguous, chronological pieces of the list.
    Left slop followed by the begin-to-end range broken into parts of step size
    followed by right slop.

    Args:
        begin (str/datetime): begin date of range, a datetime or yyyy[mm[dd[mm[ss]]]] string
        end (str/datetime): end date of range, a datetime or yyyy[mm[dd[mm[ss]]]] string
        step (str): duration to break individual Spec objects into,
            specified as \\d+[years|months|days|hours|minutes],
            for example, 5hours. If None, one Spec is returned.
        izone (str): tzdata timezone data is stored in
        qzone (str): tzdata timezone data is displayed in
        slop (str): duration to add to both ends of the partition range,
            specified as \\d+[years|months|days|hours|minutes],
            for example, 5hours
        lslop (str): duration to add to the front end of the partition range,
            specified as \\d+[years|months|days|hours|minutes],
            for example, 5hours
        rslop (str): duration to add to the back end of the partition range,
            specified as \\d+[years|months|days|hours|minutes],
            for example, 5hours
        years (str): name for years partition
        months (str): name for months partition
        days (str): name for days partition
        hours (str): name for hours partition
        minutes (str): name for hours partition

    Returns: 
       A list of hpdr.model.Spec: List representing the date range. For example,

       build_with_steps(begin='20160901', end=20161001, step=10days, --slop=1hours)

       returns a list of five Spec objects, representing these ranges:

       (YYYY=2016 AND MM=08 AND DD=31 AND HH>=23) [left slop of 1 hour]

       (YYYY=2016 AND MM=09 AND DD>=01 AND DD<11) [10 days]

       (YYYY=2016 AND MM=09 AND DD>=11 AND DD<21) [10 days]

       (YYYY=2016 AND MM=09 AND DD>=21)           [10 days]

       (YYYY=2016 AND MM=10 AND DD=01 AND HH=00)  [right slop of 1 hour]
    
    """

    keywords = {}
    if szone:
        keywords['szone'] = szone
    if dzone:
        keywords['dzone'] = dzone
    if slop:
        keywords['slop'] = slop
    if lslop:
        keywords['lslop'] = lslop
    if rslop:
        keywords['rslop'] = rslop
    if years:
        keywords['years'] = years
    if months:
        keywords['months'] = months
    if days:
        keywords['days'] = days
    if hours:
        keywords['hours'] = hours
    if minutes:
        keywords['minutes'] = minutes

    specs = []
    main_spec = Spec(begin, end, **keywords)

    if step is None:
        specs.append(main_spec)
    else:
        if not isinstance(step, timedelta):
            step = utils.deltastr_to_td(step)

        # Break into steps from begin to end, not from slop_begin
        # to slop_end, then add slop to each step
        walk_begin = main_spec.begin
        while walk_begin < main_spec.end:
            walk_end = min(main_spec.end, walk_begin + step)
            specs.append(Spec(walk_begin, walk_end, **keywords))
            walk_begin = walk_end

    return specs
