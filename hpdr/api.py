from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from .models import Spec

def build(begin,
          end,
          izone='UTC',
          qzone='UTC',
          slop=None,
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
    :param slop: (optional) duration to add to end date for partition specification,
                            specified as \d+[years|months|days|hours|minutes],
                            for example, 5hours
    :param years: (optional) name for years partition, defaults to YYYY
    :param day: (optional) name for days partition, defaults to DD
    :param hours: (optional) name for hours partition, defaults to HH
    :param minutes: (optional) name for hours partition, defaults to MIN
    :return: :class:`Spec` object representing the date range
    :rtype: :class:`Spec`
    """

    kw = {}
    if izone: kw['izone'] = izone
    if qzone: kw['qzone'] = qzone
    if slop: kw['slop'] = slop
    if years: kw['years'] = years
    if months: kw['months'] = months
    if days: kw['days'] = days
    if hours: kw['hours'] = hours
    if minutes: kw['minutes'] = minutes

    return Spec(begin,
                end,
                **kw)

          
