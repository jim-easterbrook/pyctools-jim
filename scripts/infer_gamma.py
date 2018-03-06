#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.io.plotdata
import pyctools.components.photo.infergamma
import pyctools.components.io.imagefilepil
import pyctools.components.io.rawimagefilereader
import pyctools.components.photo.canon_100d

class Network(object):
    components = \
{   'cg': {   'class': 'pyctools.components.photo.canon_100d.CanonGamma',
              'config': "{'out_vals': '  1, 30, 57, 80, "
                        "99,126,147,175,203,226,242,253,255,256', "
                        "'in_vals': '  0,  5, 10, 15, 20, 30, 40, 60, "
                        "90,130,175,225,250,275', 'smooth': True}",
              'pos': (250.0, 200.0)},
    'ifrpil': {   'class': 'pyctools.components.io.imagefilepil.ImageFileReaderPIL',
                  'config': "{'path': "
                            "'/home/jim/Pictures/from_camera/2018/2018_03_05/100D_IMG_3956.JPG'}",
                  'pos': (100.0, 50.0)},
    'ig': {   'class': 'pyctools.components.photo.infergamma.InferGamma',
              'config': '{}',
              'pos': (250.0, 50.0)},
    'pd': {   'class': 'pyctools.components.io.plotdata.PlotData',
              'config': '{}',
              'pos': (400.0, 200.0)},
    'pd0': {   'class': 'pyctools.components.io.plotdata.PlotData',
               'config': '{}',
               'pos': (400.0, 50.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': "
                          "'/home/jim/Pictures/from_camera/2018/2018_03_05/100D_IMG_3956.CR2'}",
                'pos': (100.0, 200.0)}}
    linkages = \
{   ('cg', 'function'): [('pd', 'input')],
    ('ifrpil', 'output'): [('ig', 'corr_in')],
    ('ig', 'function'): [('pd0', 'input')],
    ('rifr', 'output'): [('ig', 'linear_in'), ('cg', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':

    comp = Network().make()
    cnf = comp.get_config()
    parser = argparse.ArgumentParser()
    cnf.parser_add(parser)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase verbosity of log messages')
    args = parser.parse_args()
    logging.basicConfig(level=logging.ERROR - (args.verbose * 10))
    del args.verbose
    cnf.parser_set(args)
    comp.set_config(cnf)
    comp.start()

    try:
        comp.join(end_comps=True)
    except KeyboardInterrupt:
        pass

    comp.stop()
    comp.join()
