#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Dirk Toewe
#
# This file is part of SLeEPy.
#
# Game of Pyth is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Game of Pyth is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Game of Pyth. If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import os
import uuid
import webbrowser

from numpy import NaN, radians
from plotly import tools
import plotly
from plotly.offline.offline import get_plotlyjs
from plotly.utils import PlotlyJSONEncoder

import numpy as np
from pkg_resources import resource_string
import plotly.graph_objs as go


def meshSurface3d( uRange, vRange, f, text = 'u: {:.3f} v: {:.3f}'.format, **kwargs ):
  '''
  Creates Plot.ly 3D mesh of a sampled parametric surface.

  @param uRange: list-like. The sample points (range) of the first surface parameter.
  @param vRange: list-like. The sample points (range) of the second surface parameter.
  @param f: callable (u,v) -> (float,float,float): The function describing the surface
    for each point on the surface in parametric coordinates u,v, the function returns
    the cartesian coordinates x,y,z.
  @param text: callable (u,v) -> str: For each point on the surface in parametric
    coordinates u,v, the function returns a short text description of that point to be
    displayed when the mouse hovers over that point.
  @param kwargs: Further layout arguments, which are passed onto `plotly.graph_objs.Mesh3d`.
    The `intensity` argument can also be given in form of a `callable`, similar
    to `text`.
  @return: A `plotly.graph_objs.Mesh3d` representing the sampled parametric surface.
  '''
  if 'intensity' in kwargs:
    intensity = kwargs['intensity']
    if callable(intensity):
      kwargs['intensity'] = tuple(
        intensity(u,v)
        for u in uRange
        for v in vRange
      )

  data = np.vstack(
    f(u,v)
    for u in uRange
    for v in vRange
  )

  def idx(u,v):
    return u+v*len(uRange)
  ijk = np.vstack(
    np.array([
      [idx(u,v),  idx(u+1,v), idx(u,  v+1)],
      [idx(u,v+1),idx(u+1,v), idx(u+1,v+1)],
    ])
    for u in range(len(uRange)-1)
    for v in range(len(vRange)-1)
  )

  return go.Mesh3d(
    x = data[:,0], y = data[:,1], z = data[:,2],
    i =  ijk[:,0], j =  ijk[:,1], k =  ijk[:,2],
    **kwargs
  )

def scatterSurface3d( uRange, vRange, f, text = 'u: {:.3f} v: {:.3f}'.format, **kwargs ):
  '''
  Creates Plot.ly 3D scatter plot of a sampled parametric surface.

  @param uRange: list-like. The sample points (range) of the first surface parameter.
  @param vRange: list-like. The sample points (range) of the second surface parameter.
  @param f: callable (u,v) -> (float,float,float): The function describing the surface
    for each point on the surface in parametric coordinates u,v, the function returns
    the cartesian coordinates x,y,z.
  @param text: callable (u,v) -> str: For each point on the surface in parametric
    coordinates u,v, the function returns a short text description of that point to be
    displayed when the mouse hovers over that point.
  @param kwargs: Further layout arguments, which are passed onto `plotly.graph_objs.Scatter3d`.
    The `marker.color` and `line.color` argument can also be given in form of a `callable`,
    similar to `text`.
  @return: A `plotly.graph_objs.Scatter3d` representing the sampled parametric surface.
  '''
  for style in ['line','marker']:
    if style in kwargs:
      style = kwargs[style]
      if 'color' in style:
        color = style['color']
        if callable(color):

          def color_gen():
            for u in uRange:
              yield None # <- NaN functions as a 'line break'
              for v in vRange: yield color(u,v)
            for v in vRange:
              yield None
              for u in uRange: yield color(u,v)
  
          color_gen = color_gen()
          next(color_gen)
          style['color'] = tuple(color_gen)

  def data_gen():
    for u in uRange:
      yield NaN,NaN,NaN # <- NaN functions as a 'line break'
      for v in vRange: yield f(u,v)
    for v in vRange:
      yield NaN,NaN,NaN
      for u in uRange: yield f(u,v)

  data = data_gen()
  next(data)
  data = np.vstack(data)

  if callable(text):
    def text_gen():
      for u in uRange:
        yield '???'
        for v in vRange: yield text(u,v)
      for v in vRange:
        yield '???'
        for u in uRange: yield text(u,v)
  
    txt = text_gen()
    next(txt)
    text = tuple(txt)

  return go.Scatter3d(
    x = data[:,0], y = data[:,1], z = data[:,2],
    text = text, **kwargs
  )

plot_div_tmpl  = resource_string(__name__,"plot_div.tmpl" ).decode('utf8')

def plot_html( figure_or_data, default_width='100%', default_height='100%', config=None, validate=True ):

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

  plotly_html_div = plot_div_tmpl.format( **locals() )

  return plotly_html_div, div_id, width, height

plot_html_tmpl = resource_string(__name__,"plot_html.tmpl").decode('utf8')

def plot_file(figure_or_data, filename, auto_open=False, include_plotlyjs=True, config=None, validate=True ):
  if not filename.endswith('.html'):
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

  result = plot_html_tmpl.format( **locals() )

  with open(filename, 'w') as f:
    f.write(result)
  
  url = 'file://' + os.path.abspath(filename)
  if auto_open:
    webbrowser.open(url)

  return url