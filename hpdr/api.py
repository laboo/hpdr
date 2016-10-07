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
          ozone='UTC',          
          slop=None,
          years='YYYY',
          months='MM',
          days='DD',
          hours='HH',
          minutes='MIN'):

    kw = {}
    if izone: kw['izone'] = izone
    if ozone: kw['ozone'] = ozone
    if slop: kw['slop'] = slop
    if years: kw['years'] = years
    if months: kw['months'] = months
    if days: kw['days'] = days
    if hours: kw['hours'] = hours
    if minutes: kw['minutes'] = minutes

    return Spec(begin,
                end,
                **kw)

          
