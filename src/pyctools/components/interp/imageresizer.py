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

__all__ = ['ImageResizer2D']
__docformat__ = 'restructuredtext en'

from pyctools.components.interp.filtergenerator import FilterGenerator
from pyctools.components.interp.resize import Resize
from pyctools.core.compound import Compound

def ImageResizer2D(config={}, **kwds):
    cfg = {'xaperture': 16, 'yaperture': 16}
    cfg.update(kwds)
    cfg.update(config)
    return Compound(
        xfilgen = FilterGenerator(),
        yfilgen = FilterGenerator(),
        xresize = Resize(),
        yresize = Resize(),
        config = cfg,
        config_map = {
            'xfilgen': (('xup', 'xup'), ('xdown', 'xdown'),
                        ('xaperture', 'xaperture')),
            'yfilgen': (('yup', 'yup'), ('ydown', 'ydown'),
                        ('yaperture', 'yaperture')),
            'xresize': (('xup', 'xup'), ('xdown', 'xdown')),
            'yresize': (('yup', 'yup'), ('ydown', 'ydown')),
            },
        linkages = {
            ('self',    'input')  : ('yresize', 'input'),
            ('yfilgen', 'output') : ('yresize', 'filter'),
            ('yresize', 'output') : ('xresize', 'input'),
            ('xfilgen', 'output') : ('xresize', 'filter'),
            ('xresize', 'output') : ('self',    'output'),
            }
        )

