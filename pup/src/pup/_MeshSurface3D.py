'''
Created on Oct 2, 2016

@author: Dirk Toewe
'''
import numpy as np
import plotly.graph_objs as go


def MeshSurface3d( uRange, vRange, f, text = 'u: {:.3f} v: {:.3f}'.format, **kwargs ):
  '''
  Creates Plot.ly 3D mesh of a sampled parametric surface.

  Parameters
  ----------
  uRange: list[float]-like
    The sample points (range) of the first surface parameter.

  vRange: list[float]-like or (u: float) -> iterable[float]
    The sample points (range) of the second surface parameter, either as a fixed
    range or as a function of u. As of yet the number of sampling points in v-direction
    must be the same for every u, i.e. count(vRange(u)) = const.

  f: (u: float,v: float) -> (x: float,y: float,z: float)
    The function describing the surface for each point on the surface in parametric
    coordinates u,v, the function returns the cartesian coordinates x,y,z.

  text: (u: float,v: float) -> str
    For each point on the surface in parametric coordinates u,v, the function returns
    a short text description of that point to be displayed when the mouse hovers over
    that point.

  kwargs
    Further layout arguments, which are passed onto `plotly.graph_objs.Mesh3d`.
    The `intensity` argument can also be given in form of a `callable`, similar
    to `text`.

  Returns
  -------
  A `plotly.graph_objs.Mesh3d` representing the sampled parametric surface.
  '''

  nU = len(uRange)
  if not callable(vRange):
    _vRange = vRange
    nV = len(vRange)
    vRange = lambda u: _vRange
  else:
    nV = len( vRange(uRange[0]) )
    assert all( len( vRange(u) ) == nV for u in uRange ) # <- may however be supported in future versions

  if 'intensity' in kwargs:
    intensity = kwargs['intensity']
    if callable(intensity):
      kwargs['intensity'] = tuple(
        intensity(u,v)
        for u in uRange
        for v in vRange(u)
      )

  data = np.vstack(
    f(u,v)
    for u in uRange
    for v in vRange(u)
  )

  def idx(u,v):
    return u+v*len(uRange)
  ijk = np.vstack(
    np.array([
      [idx(u,v),  idx(u+1,v), idx(u,  v+1)],
      [idx(u,v+1),idx(u+1,v), idx(u+1,v+1)],
    ])
    for u in range(nU-1)
    for v in range(nV-1)
  )

  return go.Mesh3d(
    x = data[:,0], y = data[:,1], z = data[:,2],
    i =  ijk[:,0], j =  ijk[:,1], k =  ijk[:,2],
    **kwargs
  )