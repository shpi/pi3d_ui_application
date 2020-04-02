#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from pkg_resources import resource_filename
import numpy as np

import pi3d

from .. import config
from ..core import peripherals
from ..core import graphics

class Slice(pi3d.Shape):
  def __init__(self, camera=None, light=None, inner=0.5, outer=1, sides=36, name="",
               start=0.0, end=60, x=0.0, y=0.0, z=0.0,
               rx=0.0, ry=0.0, rz=0.0, sx=1.0, sy=1.0, sz=1.0,
               cx=0.0, cy=0.0, cz=0.0):

    super(Slice, self).__init__(camera, light, name, x, y, z, rx, ry, rz, sx, sy, sz,
                               cx, cy, cz)

    self.inner = inner
    self.outer = outer
    self.start = start
    self.end = end
    self.n = sides + 1
    (verts, texcoords) = self.make_verts()
    norms = np.zeros_like(verts)
    norms[:,2] = -1.0
    inds = np.array([[i+u, i+v, i+w] for i in range(0, 2 * self.n, 2)
                                    for (u, v, w) in [(0, 1, 3), (3, 2, 0)]], dtype=float)
    self.buf = [pi3d.Buffer(self, verts, texcoords, inds, norms)]

  def make_verts(self):
    angles = np.deg2rad(np.linspace(self.start, self.end, self.n))
    s = np.sin(angles)
    c = np.cos(angles)
    verts = np.zeros((2 * self.n, 3))
    verts[::2, 0] = s * self.inner
    verts[1::2, 0] = s * self.outer
    verts[::2, 1] = c * self.inner
    verts[1::2, 1] = c * self.outer
    texcoords = (verts[:,:2] / (2 * self.outer)) * [1, -1] + 0.5
    return (verts, texcoords)

  def reset_verts(self, inner=None, outer=None, start=None, end=None):
    if inner is not None:
      self.inner = inner
    if outer is not None:
      self.outer = outer
    if start is not None:
      self.start = start
    if end is not None:
      self.end = end
    (verts, texcoords) = self.make_verts()
    buf = self.buf[0]
    buf.array_buffer[:,0:3] = verts
    buf.array_buffer[:,6:8] = texcoords
    buf.re_init()

class Donut(object):
    def __init__(self, x=0, y=0, inner=100, outer=200, values=[], colors=[],
            full_range=None, concentric=False, start=0.0, sides=36, text_format="{:.1f}",
            camera=graphics.CAMERA, shader=graphics.MATSH):
        self.x = x
        self.y = y
        self.inner = inner
        self.outer = outer
        self.full_range = full_range
        self.concentric = concentric
        self.start = start
        self.text_format = text_format
        self.slices = []
        if full_range is None:
            full_range = sum(values)
        self.n = len(values)
        # simplest Shape only 3 vertices. z -1 so not drawn
        self.empty = pi3d.Triangle(x=x, y=y, z=-1.0)

        self.text = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                        max_chars=(self.n * 20), point_size=64)
        tot = self.start
        step = (outer - inner) / self.n
        for i in range(self.n):
            end = 360 * values[i] / full_range
            if concentric:
                a_slice = Slice(camera=camera, inner=inner + i * step,
                        outer=inner + (i + 1) * step, sides=sides, start=self.start,
                        end=end, z=3.0) #z=3 to compensate for empty set to -1 and draw behind labels
            else:
                a_slice = Slice(camera=camera, inner=inner, outer=outer,
                    start=tot, end=tot + end, z=3.0)
                tot += end
            buf = a_slice.buf[0].array_buffer # alias for brevity
            midv = len(buf) // 2 # text half way round curve, miday between inner and outer
            text_x = (buf[midv, 0] + buf[midv + 1, 0]) / 2 + self.x
            text_y = (buf[midv, 1] + buf[midv + 1, 1]) / 2 + self.y
            slice_text = pi3d.TextBlock(text_x, text_y, 0.0, 0.0, 15,
                            text_format=self.text_format.format(values[i]),
                            size=0.5, spacing="C", space=0.6, justify=0.5)
            self.text.add_text_block(slice_text)
            a_slice.set_shader(shader)
            a_slice.set_material(colors[i])
            self.slices.append(a_slice)
            self.empty.add_child(a_slice)


    def update(self, values):
        (inner, outer) = (None, None)
        start = self.start
        tot = start
        step = (self.outer - self.inner) / self.n
        full_range = sum(values) if self.full_range is None else self.full_range
        for i in range(len(values)):
            end = 360 * values[i] / full_range
            if self.concentric:
                inner = self.inner + i * step
                outer = inner + step
            else:
                start = tot
                tot += end
            self.slices[i].reset_verts(inner=inner, outer=outer, start=start, end=start + end)
            buf = self.slices[i].buf[0].array_buffer # alias for brevity
            midv = len(buf) // 2
            text_x = (buf[midv, 0] + buf[midv + 1, 0]) / 2 + self.x
            text_y = (buf[midv, 1] + buf[midv + 1, 1]) / 2 + self.y
            block = self.text.text_blocks[i] # use the fact blocks store in same order as vaues
            block.set_position(x=text_x, y=text_y)
            block.set_text(self.text_format.format(values[i]))
        self.text.regen()


    def draw(self):
        self.empty.draw()
        self.text.draw()