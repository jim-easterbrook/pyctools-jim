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

__all__ = ['CanonGamma']
__docformat__ = 'restructuredtext en'

import numpy

from pyctools.components.colourspace.gammacorrection import PiecewiseGammaCorrect

def CanonGamma(config={}, **kwds):
    """Gamma correction function reverse engineered from a Canon EOS
    100D camera. See also
    pyctools.components.colourspace.gammacorrection.PiecewiseGammaCorrect"""
    return PiecewiseGammaCorrect(
        in_vals= '0,  5, 10, 15, 20, 30, 40, 60, 90,130,170,210,250,270',
        out_vals='0, 30, 56, 80, 99,126,147,176,204,226,240,250,256,257',
        smooth=True, config=config, **kwds)
