'''
Created on Oct 15, 2016

@author: Dirk Toewe
'''

from pandas import read_csv
from pup._plot_pandas import plot_DataFrame_html, plot_DataFrame_file
import plotly.graph_objs as go
from pandas.core.frame import DataFrame

dataFrame = read_csv('frankfurt_weather.csv', delimiter=';', skipinitialspace=True)
dataFrame = dataFrame[ dataFrame['MESS_DATUM'] >= 20140101 ]
dataFrame = dataFrame[ dataFrame['MESS_DATUM'] <= 20141231 ]
# print(dataFrame)

print(
  plot_DataFrame_file(
    dataFrame,
    layout = dict(
      margin = dict( l=0, r=0, b=0, t=16, pad=0 ),
      height=800
    )
  )
)