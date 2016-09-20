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

from tempfile import NamedTemporaryFile

from numpy import radians

import numpy as np
import plotly.graph_objs as go
from pup import meshSurface3d
import pup


def main():

  surface = meshSurface3d(
    np.linspace(-2,+2,11),
    np.linspace(-1,+1,11),
    lambda u,v: (u,v,u*v),
    intensity = lambda u,v: u*v,
    colorbar=go.ColorBar(
      title='Z-Value'
    ),
    colorscale='Viridis',
    opacity=0.75,
    name = 'Surface'
  )
  
  sin = lambda x: np.sin(radians(x))
  cos = lambda x: np.cos(radians(x))
  
  sphere = meshSurface3d(
    np.linspace(  0, 360, 19),
    np.linspace(-90, +90, 19),
    lambda u,v: ( cos(u)*cos(v), sin(u)*cos(v), sin(v) ),
    color='#0000FF',
    opacity=0.75,
    name = 'Sphere'
  )
  
  layout = go.Layout(
    title='Wireframe Plot',
    scene = dict(
      aspectratio = dict(x=1, y=1, z=1),
      aspectmode = 'data'
    )
  )
  
  fig = go.Figure(data=[surface,sphere],layout=layout)
  pup.plot_file(fig, filename=NamedTemporaryFile(prefix='MeshSurface3D_',suffix='.html').name, auto_open=True)

if __name__ == '__main__':
  main()