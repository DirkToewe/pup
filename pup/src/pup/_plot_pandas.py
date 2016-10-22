'''
Created on Oct 15, 2016

@author: Dirk Toewe
'''
from base64 import b64encode
import io, json
from zipfile import ZIP_DEFLATED, ZipFile

from pkg_resources import resource_string

import plotly.graph_objs as go
import uuid
from tempfile import NamedTemporaryFile
import logging
from plotly.offline.offline import get_plotlyjs
import webbrowser
import os

_plot_DataFrame_div_template  = resource_string(__name__,"plot_DataFrame_div.template" ).decode('utf8')
_plot_DataFrame_file_template = resource_string(__name__,"plot_DataFrame_file.template").decode('utf8')
jszip_min_js = resource_string(__name__,'jszip.min.js').decode('utf8')

def plot_DataFrame_html( dataFrame, layout={}, config=None, zipped=True, validate=True ):

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

  jData = { k:list(v) for k,v in dataFrame.iteritems() }
  jData = json.dumps(jData)
  jLayout = json.dumps(layout)
  jConfig = json.dumps(config)
  jColumns= json.dumps( list(dataFrame.columns) )
  jIndex  = json.dumps( list(dataFrame.index) )

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
    zipFile.writestr('/data.json', jData)
    zipFile.writestr('/index.json', jIndex)
    zipFile.writestr('/columns.json', jColumns)
  zDataFrame = b64encode( zDataFrame.getvalue() ).decode('utf-8')
  div = _plot_DataFrame_div_template.format( **locals() )

  return div, div_id, width, height

def plot_DataFrame_file( dataFrame, layout={}, filename=None, auto_open=True, config=None, zipped=True, include_plotlyjs=True, validate=True ):

  if None is filename:
    with NamedTemporaryFile(prefix='tmp_plot_',suffix='.html',delete=False) as file:
      filename = file.name
  elif not filename.endswith('.html'):
    logging.warn( 'Your filename "%s" doesn\'t end with .html.', filename)

  plot_div, div_id, width, height = plot_DataFrame_html(dataFrame, layout, config=config, zipped=zipped, validate=validate )
  plotly_script = '' if not include_plotlyjs else '<script type="text/javascript">' + get_plotlyjs() + '</script>'
  if zipped:
    plotly_script += '<script type="text/javascript">' + jszip_min_js + '</script>'
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