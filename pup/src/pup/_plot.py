'''
Created on Oct 2, 2016

@author: Dirk Toewe
'''
import json, logging, os, uuid, webbrowser

from pkg_resources import resource_string
from plotly import tools
from plotly.offline.offline import get_plotlyjs
from plotly.utils import PlotlyJSONEncoder
from tempfile import NamedTemporaryFile


_plot_file_template = resource_string(__name__,"plot_file.template").decode('utf8')
_plot_div_template  = resource_string(__name__,"plot_div.template" ).decode('utf8')

def plot_html( figure_or_data, default_width='100%', default_height='100%', validate=True, config=None ):
  '''
  Creates an HTML-div string visualizing the fiven Plotly figure.

  Parameters
  ----------
  figure_or_data
    The Plotly figure to be embedded into HTML.
  default_width
    If the figure does not have a defined width, the `default_width` is being used.
  default_height
    If the figure does not have a defined width, the `default_height` is being used.
  validate
    Whether or not the figure is to be checked for validity
  config
    The config object to be used in the Plotly JavaScript graph code.

  Returns
  -------
  HTML div as str, which can be embedded into HTML-pages to visualize `figure_or_data`.
  Does not include the Plotly JavaScript code.
  '''
  figure = tools.return_figure_from_figure_or_data(figure_or_data, validate)

  def with_units(x):
    try:
      float(x)
    except (ValueError, TypeError):
      return x
    else:
      return str(x) + 'px'
  width  = figure.get('layout', {}).get('width',  default_width )
  height = figure.get('layout', {}).get('height', default_height)
  width  = with_units(width )
  height = with_units(height)

  if None is config:
    config = dict(
      showLink=False,
      linkText='',
      modeBarButtonsToRemove = ['sendDataToCloud']
    )
  jconfig = json.dumps(config)
  jdata   = json.dumps(figure.get('data',   []), cls=PlotlyJSONEncoder)
  jlayout = json.dumps(figure.get('layout', {}), cls=PlotlyJSONEncoder)
  div_id = uuid.uuid4()

  plotly_html_div = _plot_div_template.format( **locals() )

  return plotly_html_div, div_id, width, height

def plot_file(figure_or_data, filename=None, auto_open=True, include_plotlyjs=True, validate=True, config=None ):
  '''
  Creates an HTML-file visualizing the fiven Plotly figure.

  Parameters
  ----------
  figure_or_data
    The Plotly figure to be embedded into HTML.
  filename
    The filepath to write to. If the file alread exists, it is being overwritten.
  auto_open: bool
    If set to True, the file is opened in the browser.
  include_plotlyjs: bool
    Whether or not to include the Plotly JavaScript library in the HTML-file.
  validate
    Whether or not the figure is to be checked for validity
  config
    The config object to be used in the Plotly JavaScript graph code.

  Returns
  -------
  HTML file which can be opened in any modern browser to view the figure.
  '''
  if None is filename:
    with NamedTemporaryFile(prefix='tmp_plot_',suffix='.html',delete=False) as file:
      filename = file.name
  elif not filename.endswith('.html'):
    logging.warn( 'Your filename "%s" doesn\'t end with .html.', filename)

  plot_div, div_id, width, height = plot_html(figure_or_data, config=config, validate=validate )
  plotly_script = '' if not include_plotlyjs else '<script type="text/javascript">' + get_plotlyjs() + '</script>'
  resize_script = '' if width != '100%' and height == '100%' else (
  '''
    <script type="text/javascript">
      window.removeEventListener("resize");
      window.addEventListener("resize", function(){{
      Plotly.Plots.resize(document.getElementById("{div_id}"));}});
    </script>'
  '''.format(div_id=div_id)
  )

  result = _plot_file_template.format( **locals() )

  with open(filename, 'w') as f:
    f.write(result)
  
  url = 'file://' + os.path.abspath(filename)
  if auto_open:
    webbrowser.open(url)

  return url