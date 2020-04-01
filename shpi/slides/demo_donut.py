#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import pi3d
from pkg_resources import resource_filename
import random

from .. import config
from ..core import peripherals
from ..core import graphics

from ..core.donut import Donut

values = [50, 100, 125, 60, 15]
colors = [[1.0, 1.0, 0.2], [0.5, 0.7, 0.5], [0.0, 0.5, 1.0], [1.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
donut = Donut(values=values, colors=colors, concentric=False, start=-90)
#donut = Donut(values=values, colors=colors, concentric=True, full_range=400, start=-90)
count = 0

def inloop(textchange=False, activity=False, offset=0):
    global values, count

    donut.draw()

    count += 1
    if count % 30 == 0:
        values = [v * (0.9 + random.random() * 0.2) for v in values]
        donut.update(values)
    else:
        for s in donut.slices:
            os = graphics.slider_change(s, offset)
        offset = os # last one.

    activity = True
    return activity, offset
