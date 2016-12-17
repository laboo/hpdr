# pylint: disable=too-many-arguments
"""Doco
"""
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
          izone='UTC',
          qzone='UTC',
          slop=None,
          lslop=None,
          rslop=None,
          years='YYYY',
          months='MM',
          days='DD',
          hours='HH',
          minutes='MIN'):
    """Build a specification for a date range.

    :param begin: begin date of range, a datetime or yyyymmddmmss string
    :param end: end date of range, a datetime or yyyymmddmmss string
    :param izone: (optional) time zone for input dates, defaults to UTC
    :param qzone: (optional) time zone to use in query, defaults to UTC
    :param slop: (optional) duration to add to both ends of the partition range,
                            specified as \\d+[years|months|days|hours|minutes],
                            for example, 5hours
    :param lslop: (optional) duration to add to the front end of the partition range,
                            specified as \\d+[years|months|days|hours|minutes],
                            for example, 5hours
    :param rslop: (optional) duration to add to the back end of the partition range,
                            specified as \\d+[years|months|days|hours|minutes],
                            for example, 5hours
    :param years: (optional) name for years partition, defaults to YYYY
    :param months: (optional) name for months partition, defaults to MM
    :param days: (optional) name for days partition, defaults to DD
    :param hours: (optional) name for hours partition, defaults to HH
    :param minutes: (optional) name for hours partition, defaults to MIN
    :return: :class:`Spec` object representing the date range
    :rtype: :class:`Spec`
    """
    keywords = {}
    if izone:
        keywords['izone'] = izone
    if qzone:
        keywords['qzone'] = qzone
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

    specs = build_with_steps(begin,
                             end,
                             keywords['izone'] if izone in keywords else None,
                             keywords['qzone'] if qzone in keywords else None,
                             keywords['slop'] if slop in keywords else None,
                             keywords['lslop'] if lslop in keywords else None,
                             keywords['rslop'] if rslop in keywords else None,
                             keywords['years'] if years in keywords else None,
                             keywords['months'] if months in keywords else None,
                             keywords['days'] if days in keywords else None,
                             keywords['hours'] if hours in keywords else None,
                             keywords['minutes'] if minutes in keywords else None)

    return specs[0]


def build_with_steps(begin,
                     end,
                     step=None,
                     izone='UTC',
                     qzone='UTC',
                     slop=None,
                     lslop=None,
                     rslop=None,
                     years='YYYY',
                     months='MM',
                     days='DD',
                     hours='HH',
                     minutes='MIN'):
    """Build a specification for a date range.

    :param begin: begin date of range, a datetime or yyyymmddmmss string
    :param end: end date of range, a datetime or yyyymmddmmss string
    :param izone: (optional) time zone for input dates, defaults to UTC
    :param qzone: (optional) time zone to use in query, defaults to UTC
    :param slop: (optional) duration to add to both ends of the partition range,
                            specified as \\d+[years|months|days|hours|minutes],
                            for example, 5hours
    :param lslop: (optional) duration to add to the front end of the partition range,
                            specified as \\d+[years|months|days|hours|minutes],
                            for example, 5hours
    :param rslop: (optional) duration to add to the back end of the partition range,
                            specified as \\d+[years|months|days|hours|minutes],
                            for example, 5hours
    :param years: (optional) name for years partition, defaults to YYYY
    :param months: (optional) name for months partition, defaults to MM
    :param days: (optional) name for days partition, defaults to DD
    :param hours: (optional) name for hours partition, defaults to HH
    :param minutes: (optional) name for hours partition, defaults to MIN
    :return: :class:`Spec` object representing the date range
    :rtype: :class:`Spec`
    """

    keywords = {}
    if izone:
        keywords['izone'] = izone
    if qzone:
        keywords['qzone'] = qzone
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
        keywords['slop'] = keywords['lslop'] = keywords['rslop'] = None
        if not isinstance(step, timedelta):
            step = utils.deltastr_to_td(step)
        specs.append(Spec(main_spec.slop_begin, main_spec.begin, **keywords))
        walk_begin = main_spec.begin
        while walk_begin < main_spec.end:
            walk_end = min(main_spec.end, walk_begin + step)
            specs.append(Spec(walk_begin, walk_end, **keywords))
            walk_begin = walk_end
        specs.append(Spec(main_spec.end, main_spec.slop_end, **keywords))

    return specs
