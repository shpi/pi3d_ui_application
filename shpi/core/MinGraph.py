#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

from pi3d import opengles, GLfloat
import pi3d
import numpy as np
import logging

LOGGER = logging.getLogger(__name__)

class MinGraph(object):
    """Providing some basic functionality for a GPU accelerated x, y graph
    (i.e. for real-time display of instrumentation data etc)"""
    def __init__(self, x_values, y_values, width, height,  xpos=0, ypos=0,z = 1.0,
                  xmin=None, xmax=None, ymin=None, ymax=None, camera=None,
                  shader=None, colorarray = [(0,0,1,1,1),(1,0,0,1,1),(0,1,0,1,1)]):
        """
        Arguments:
            *x_values*
                1D numpy array
            *y_values*
                1 or 2D numpy array with size same as x_values in 2nd D draws
                a line graph
                or 3D numpy array with size same as x along axis=1 and last axis
                has 2 values. In this case the graph is drawn as vertical lines
            *width, height*
                as expected
            *font*
                pi3d.Font instance
            *title, line_width*
                as expected
            *axes_desc*
                tuple -> (x.axis.desc, y.axis.desc)
            *legend*
                tuple -> (y0.desc, y1.desc, y2.desc...)
            *xpos, ypos*
                offset relative to origin of display (centre)
            *xmin, xmax, ymin, ymax*
                override sampled values from init data
            *camera*
                if no other Shape to be drawn then a 2D Camera can be created here
            *shader*
                if no other Shape uses mat_flat shader then one will be created
        """
        if len(y_values.shape) < 2:
            y_values.shape = (1,) + y_values.shape
        if x_values.shape[0] != y_values.shape[1]:
            LOGGER.error('mismatched array lengths')
            return
        if camera is None:
            camera = pi3d.Camera(is_3d=False)
        if shader is None:
            shader = pi3d.Shader('mat_flat')
        # axes ###########
        axex, axey = width * 0.5, height * 0.5 # implies 10% margin all round
        # lines to represent data
        n = x_values.shape[-1]
        if xmin is None:
            xmin = x_values.min()
        if xmax is None:
            xmax = x_values.max()
        x_factor =  (2.0 * axex) / (xmax - xmin)
        x_offset = xmin
        if ymin is None:
            ymin = y_values.min()
        if ymax is None:
            ymax = y_values.max()
        y_factor =  (2.0 * axey) / (ymax - ymin)
        y_offset = ymin
        self.lines = []
        for i in range(y_values.shape[0]):
            data = np.zeros((n, 3))
            data[:,0] = (x_values - x_offset) * x_factor - axex + xpos
            if len(y_values[i].shape) == 1: # i.e. normal line graph
                data[:,1] = (y_values[i] - y_offset) * y_factor - axey + ypos
                strip = True
            else: # has to be pairs of values for separate line segments
                xx_vals = np.stack([data[:,0], data[:,0]], axis=1).ravel() # make x into pairs
                data = np.zeros((n * 2, 3))
                data[:,0] = xx_vals
                data[:,1] = (y_values[i].ravel() - y_offset) * y_factor - axey + ypos
                strip = False
            data[:,2] = z # z value
            rgb_val = colorarray[i]
            line = pi3d.Lines(vertices=data, line_width=rgb_val[4], z = (z-i*0.01), strip=strip)
            line.set_shader(shader)
            j = i + 2
            #rgb_val = tuple(int(i * 255) for i in colorarray[i]) # converting 0..1 -> 0 -255
            line.set_material((rgb_val[0],rgb_val[1],rgb_val[2]))
            line.set_alpha(rgb_val[3])
            self.lines.append(line)
        # scale factors for use in update() so add to self
        self.y_offset = y_offset
        self.y_factor = y_factor
        self.axey = axey
        self.ypos = ypos

    def draw(self):
        for line in self.lines:
            opengles.glLineWidth(GLfloat(line.buf[0].unib[11]))
            line.draw()

    def update(self, y_values):
        """ update all y_values
        """
        if len(y_values.shape) < 2: # in case single line
            y_values.shape = (1,) + y_values.shape
        for i in range(y_values.shape[0]):
            self.lines[i].buf[0].array_buffer[:,1] = (y_values[i].ravel() - self.y_offset) * self.y_factor - self.axey + self.ypos
            self.lines[i].re_init()