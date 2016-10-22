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
Created on Oct 2, 2016

@author: Dirk Toewe
'''
from numpy import NaN

import numpy as np
import plotly.graph_objs as go


def ScatterSurface3d( uRange, vRange, f, text = 'u: {:.3f} v: {:.3f}'.format, **kwargs ):
  '''
  Creates Plot.ly 3D scatter plot of a sampled parametric surface.

  uRange: list[float]-like
    The sample points (range) of the first surface parameter.

  vRange: list[float]-like or (u: float) -> iterable[float]
    The sample points (range) of the second surface parameter, either as a fixed
    range or as a function of u. As of yet the number of sampling points in v-direction
    must be the same for every u, i.e. len(vRange(u)) = const.

  f: (u: float,v: float) -> (x: float,y: float,z: float)
    The function describing the surface for each point on the surface in parametric
    coordinates u,v, the function returns the cartesian coordinates x,y,z.

  text: (u: float,v: float) -> str
    For each point on the surface in parametric coordinates u,v, the function returns
    a short text description of that point to be displayed when the mouse hovers over
    that point.

  kwargs
    Further layout arguments, which are passed onto `plotly.graph_objs.Scatter3d`.
    The `marker.color` and `line.color` argument can also be given in form of a `callable`,
    similar to `text`.

  Returns
  -------
  A `plotly.graph_objs.Scatter3d` representing the sampled parametric surface.
  '''

  nU = len(uRange)
  if not callable(vRange):
    _vRange = vRange
    nV = len(vRange)
    vRange = lambda u: _vRange
  else:
    nV = len( vRange(uRange[0]) )
    assert all( len( vRange(u) ) == nV for u in uRange ) # <- may however be supported in future versions

  def to_surface( separator, values ):
    for u in range(nU):
      if 0 != u:
        yield separator
      yield from values[nV*u:nV*(u+1)]
    for v in range(nV):
      yield separator
      yield from values[v::nV]

  for style in ['line','marker']:
    if style in kwargs:
      style = kwargs[style]
      if 'color' in style:
        color = style['color']
        if callable(color):
  
          style['color'] = list(
            to_surface(None,[
              color(u,v)
              for u in uRange
              for v in vRange(u)
            ])
          )

  data = np.vstack(
    to_surface( (NaN,NaN,NaN), [
      f(u,v)
      for u in uRange
      for v in vRange(u)
    ])
  )

  if callable(text):
    text = list(
      to_surface(None,[
        text(u,v)
        for u in uRange
        for v in vRange(u)
      ])
    )

  return go.Scatter3d(
    x = data[:,0], y = data[:,1], z = data[:,2],
    text = text, **kwargs
  )