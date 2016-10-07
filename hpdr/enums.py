from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import enum

class Position(enum.IntEnum):
  left = 0
  middle = 1
  right = 2

class Level(enum.IntEnum):
  YYYY = 0
  MM = 1
  DD = 2
  HH = 3
  MIN = 4
  
