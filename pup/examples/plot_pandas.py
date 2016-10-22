# Copyright 2016 Dirk Toewe
#
# This file is part of PUP.
#
# PUP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PUP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PUP. If not, see <http://www.gnu.org/licenses/>.
'''
Created on Oct 15, 2016

@author: Dirk Toewe
'''

from pandas import read_csv
from pup._plot_pandas import plot_DataFrame_file

def main():
  # SOURCE: www.dwd.de (Deutscher Wetterdienst)
  dataFrame = read_csv('frankfurt_weather.csv', delimiter=';', skipinitialspace=True)
  del dataFrame['eor']
  plot_DataFrame_file(
    dataFrame,
    layout = {
      'margin': dict( l=0, r=0, b=0, t=16, pad=0 ),
      'height': 800
    }
  )

if '__main__' == __name__:
  main()