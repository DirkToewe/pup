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
from base64 import b64encode
import io, json, logging, numpy as np, os, uuid, webbrowser
from json.encoder import JSONEncoder
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

from numpy import issubdtype
from pandas import Series, Index, DataFrame
from pkg_resources import resource_string
from plotly.offline.offline import get_plotlyjs

import plotly.graph_objs as go


_plot_DataFrame_div_template  = resource_string(__name__,"plot_DataFrame_div.template" ).decode('utf8')
_plot_DataFrame_file_template = resource_string(__name__,"plot_DataFrame_file.template").decode('utf8')
_jszip_min_js = resource_string(__name__,'jszip.min.js').decode('utf8')

class _DataFrameJSONEncoder(JSONEncoder):
 
  def default(self, obj):
    if isinstance(obj,DataFrame): 
      return {
        'columns': obj.columns,
        'index': obj.index,
        'data': { k:v for k,v in obj.items() }
      }
    if isinstance(obj,Index):
      obj = obj.to_series()
    if isinstance(obj,Series):
      return (
        [ int(i) for i in obj ]
        if issubdtype( obj.dtype, np.integer ) else      
        list(obj)
      )
    JSONEncoder.default(self, obj)
_DataFrameJSONEncoder = _DataFrameJSONEncoder()

def plot_DataFrame_html( dataFrame, layout={}, config=None, zipped=True, validate=True ):
  '''
  '''
  assert zipped

  if not isinstance(layout,go.Layout):
    layout = go.Layout(**layout)

  for axis in ['xaxis','yaxis']:
    if axis in layout and 'title' in layout[axis]:
      logging.warning('ignoring layout.%s.title',axis)
  if 'scene' not in layout:
    layout['scene'] = {}
  scene = layout['scene']
  for axis in ['xaxis','yaxis','zaxis']:
    if axis in scene:
      if 'title' in scene[axis]:
        logging.warning('ignoring layout.scene.%s.title',axis)
    else:
      scene[axis] = {}

  scene['xaxis']['title'] = 'x'
  scene['yaxis']['title'] = 'y'
  scene['zaxis']['title'] = 'z'

  jLayout = json.dumps(layout)
  jConfig = json.dumps(config)
  jDataFrame = _DataFrameJSONEncoder.encode(dataFrame)

  def with_units(x):
    try:
      float(x)
    except (ValueError, TypeError):
      return x
    else:
      return str(x) + 'px'
  width  = layout.get('width', '100%')
  height = layout.get('height','100%')
  width  = with_units(width )
  height = with_units(height)

  div_id = uuid.uuid4()

  zDataFrame = io.BytesIO()
  with ZipFile(zDataFrame,'w',compression=ZIP_DEFLATED) as zipFile:
    zipFile.writestr('/dataFrame.json', jDataFrame)
  zDataFrame = b64encode( zDataFrame.getvalue() ).decode('utf-8')
  div = _plot_DataFrame_div_template.format( **locals() )

  return div, div_id, width, height

def plot_DataFrame_file( dataFrame, scatter3d={}, layout={}, filename=None, auto_open=True, config=None, zipped=True, include_plotlyjs=True, validate=True ):
  '''
  '''
  if None is filename:
    with NamedTemporaryFile(prefix='tmp_plot_',suffix='.html',delete=False) as file:
      filename = file.name
  elif not filename.endswith('.html'):
    logging.warn( 'Your filename "%s" doesn\'t end with .html.', filename)

  plot_div, div_id, width, height = plot_DataFrame_html(dataFrame, layout, config=config, zipped=zipped, validate=validate )
  plotly_script = '' if not include_plotlyjs else '<script type="text/javascript">' + get_plotlyjs() + '</script>'
  if zipped:
    plotly_script += '<script type="text/javascript">' + _jszip_min_js + '</script>'
  resize_script = '' if width != '100%' and height == '100%' else (
  '''
    <script type="text/javascript">
      window.removeEventListener("resize");
      window.addEventListener("resize", function(){{
      Plotly.Plots.resize(document.getElementById("{div_id}"));}});
    </script>'
  '''.format(div_id=div_id)
  )

  result = _plot_DataFrame_file_template.format( **locals() )

  with open(filename,'w') as f:
    f.write(result)
  
  url = 'file://' + os.path.abspath(filename)
  if auto_open:
    webbrowser.open(url)

  return url

  def iplot_DataFrame():
    raise Exception('Not yet implemented!')