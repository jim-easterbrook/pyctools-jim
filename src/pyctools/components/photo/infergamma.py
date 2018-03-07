#  Pyctools-Jim - miscellaneous pyctools components that aren't good enough
#  for general use.
#  http://github.com/jim-easterbrook/pyctools-jim
#  Copyright (C) 2018  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
#  This program is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.

__all__ = ['InferGamma']
__docformat__ = 'restructuredtext en'

import numpy

from pyctools.core.base import Component
from pyctools.core.types import pt_float


class InferGamma(Component):
    """Compares two inputs and derives a gamma function for each
    component."""

    inputs = ['corr_in', 'linear_in']
    outputs = ['function']

    def process_frame(self):
        # get inputs
        corr_in = self.input_buffer['corr_in'].get()
        linear_in = self.input_buffer['linear_in'].get()
        cor_data = corr_in.as_numpy(dtype=pt_float)
        lin_data = linear_in.as_numpy(dtype=pt_float)
        h, w, comps = cor_data.shape
        func_data = [numpy.arange(256, dtype=pt_float)]
        for comp in range(comps):
            # sort data
            cor_sort = numpy.sort(cor_data[:,:,comp], axis=None)
            lin_sort = numpy.sort(lin_data[:,:,comp], axis=None)
            # find corresponding values
            y_value = numpy.empty_like(func_data[0])
            idx = 0
            for i in range(func_data[0].shape[0]):
                while idx < lin_sort.shape[0] and lin_sort[idx] < func_data[0][i]:
                    idx += 1
                lo = idx - 1
                hi = idx
                while hi < lin_sort.shape[0] and lin_sort[hi] <= func_data[0][i]:
                    hi += 1
                # lo points to highest value that is lower than target
                # hi points to lowest value that is greater than target
                if hi - lo > 1:
                    # move to middle of multiple duplicate values
                    adj = (hi - lo) // 2
                    lo += adj
                    hi -= adj
                x_points = []
                y_points = []
                if lo >= 0:
                    x_points.append(lin_sort[lo])
                    y_points.append(cor_sort[lo])
                if hi > lo and hi < lin_sort.shape[0]:
                    x_points.append(lin_sort[hi])
                    y_points.append(cor_sort[hi])
                y_value[i] = y_points[0]
                if len(x_points) == 2:
                    # linear interp
                    if x_points[1] == x_points[0]:
                        alpha = 0.5
                    else:
                        alpha = ((func_data[0][i] - x_points[0]) /
                                     (x_points[1] - x_points[0]))
                    y_value[i] += alpha * (y_points[1] - y_points[0])
                print(x_points[0], y_points[0])
            func_data.append(y_value)
        # send to function output
        func_frame = self.outframe_pool['function'].get()
        func_frame.data = numpy.stack(func_data)
        func_frame.type = 'func'
        func_frame.metadata.set(
            'labels', str(['gamma curve', 'R', 'G', 'B']))
        self.send('function', func_frame)
