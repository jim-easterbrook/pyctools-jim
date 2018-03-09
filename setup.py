#!/usr/bin/env python
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

import os
from setuptools import setup
import sys

from pyctools.setup import find_packages, write_init_files

version = '0.1.0'

# find packages
packages = find_packages()
print(packages)

# make sure each package is a "namespace package"
write_init_files(packages)

with open('README.rst') as f:
    long_description = f.read()
url = 'https://github.com/jim-easterbrook/pyctools-jim'

setup(name = 'pyctools.jim',
      version = version,
      author = 'Jim Easterbrook',
      author_email = 'jim@jim-easterbrook.me.uk',
      url = url,
      description = 'Miscellaneous Pyctools components',
      long_description = long_description,
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Multimedia :: Video',
          'Topic :: Scientific/Engineering :: Image Recognition',
          'Topic :: Scientific/Engineering :: Visualization',
          ],
      license = 'GNU GPL',
      platforms = ['POSIX', 'MacOS'],
      packages = packages,
      package_dir = {'' : 'src'},
      install_requires = ['pyctools.core'],
      zip_safe = False,
      )
