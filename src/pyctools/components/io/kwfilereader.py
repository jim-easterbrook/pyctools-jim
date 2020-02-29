#  Pyctools - a picture processing algorithm development kit.
#  http://github.com/jim-easterbrook/pyctools
#  Copyright (C) 2020  Jim Easterbrook
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

__all__ = ['KWFileReader']
__docformat__ = 'restructuredtext en'

from collections import namedtuple
import enum
import io
import os
import struct

import numpy

from pyctools.core.config import ConfigPath, ConfigEnum
from pyctools.core.base import Component
from pyctools.core.frame import Metadata
from pyctools.core.types import pt_float


PicFile = namedtuple('PicFile',
                     ('comps', 'interleave',
                      'chroma_phase',
                      'full_width', 'full_height',
                      'field_freq', 'interlace',
                      'active_width', 'active_height',
                      'aspect_width', 'aspect_height',
                      'acc_bits', 'over_bits',
                      'min_lum', 'max_lum',
                      'min_chrom', 'max_chrom',
                      'pos_x', 'pos_y', 'pos_z',
                      'len_x', 'len_y', 'len_z',
                      'pic_name',
                      'code',
                      'data_type',
                      'precision'))
PicFile_fmt = '23i80s4sii'


class DataTypes(enum.Enum):
    ps_tng_KW = 0
    ps_tng_REAL = 1
    ps_tng_BITPIPE = 2
    ps_tng_INT = 3
    ps_tng_SHORT = 4
    ps_tng_BYTE = 5


class KWFileReader(Component):
    """Read "Kingswood picture files".

    This component reads a subset of the very flexible "Kingswood
    picture file" format used from the 1980s on at BBC Research.

    ===========  ===  ====
    Config
    ===========  ===  ====
    ``path``     str  Path name of file to be read.
    ===========  ===  ====

    """

    inputs = []
    outputs = ['output']    #:

    def initialise(self):
        self.config['path'] = ConfigPath()

    def on_start(self):
        # create file reader
        self.frame_no = 0
        self.generator = self.file_reader()

    def process_frame(self):
        frame = self.outframe_pool['output'].get()
        frame.data = next(self.generator)
        frame.metadata.copy(self.metadata)
        frame.frame_no = self.frame_no
        self.frame_no += 1
        frame.type = self.frame_type
        self.send('output', frame)

    def file_reader(self):
        self.update_config()
        path = self.config['path']
        # open file
        with open(path, 'rb') as pf:
            # read header
            preamble = pf.read(1)
            if preamble[0] == 16:
                # KW picture file
                big_endian = False
                header, audit_lines = self.read_kw_header(pf)
                shape = header.len_y, header.len_x, header.comps
                swap_axes = False
            else:
                preamble += pf.read(7)
                if preamble == b'PIC-PIPE':
                    # big endian pic pipe
                    big_endian = True
                elif preamble == b'PIC-pipe':
                    # small endian pic pipe
                    big_endian = False
                else:
                    print('Unrecognised header', preamble)
                    return
                # read header
                count = int.from_bytes(
                    pf.read(4), byteorder=('little', 'big')[big_endian],
                    signed=True)
                pf.read(4)
                header_struct = struct.Struct(
                    ('<', '>')[big_endian] + PicFile_fmt)
                header = PicFile(*header_struct.unpack(pf.read(count - 4)))
                header = header._replace(
                    pic_name=header.pic_name.decode('ascii').strip('\0'),
                    code=header.code.decode('ascii').strip('\0'),
                    data_type=DataTypes(header.data_type))
                shape = header.len_y, header.comps, header.len_x
                swap_axes = True
                # read audit trail
                audit_lines = []
                while True:
                    count = int.from_bytes(
                        pf.read(4), byteorder=('little', 'big')[big_endian],
                        signed=True)
                    if count == 0:
                        break
                    audit_lines.append(pf.read(80)[:count].decode('ascii'))
            print(header)
            if header.interleave != 1:
                print('Cannot read interleave', header.interleave)
                return
            if header.data_type == DataTypes.ps_tng_KW:
                bytes_per_sample = (((header.over_bits + 7) // 8)
                                    + 1 + ((header.acc_bits + 7) // 8))
            elif header.data_type == DataTypes.ps_tng_BYTE:
                bytes_per_sample = 1
            elif header.data_type == DataTypes.ps_tng_SHORT:
                bytes_per_sample = 2
            else:
                print('Cannot read', header.data_type.name)
                return
            self.frame_type = header.code
            self.metadata = Metadata()
            audit = '{} = '.format(os.path.basename(path))
            indent = 0
            for line in audit_lines:
                if line[0] == '{':
                    indent += 1
                if audit[-1] == '\n':
                    audit += ('    ' * indent)
                audit += line + '\n'
                if '}' in line:
                    indent -= 1
            audit += 'data = KWFileReader({})\n'.format(os.path.basename(path))
            audit += self.config.audit_string()
            self.metadata.set('audit', audit)
            # read data
            bytes_per_frame = (header.len_y * header.len_x
                               * header.comps * bytes_per_sample)
            for z in range(header.len_z):
                raw_data = pf.read(bytes_per_frame)
                # convert to numpy array
                if bytes_per_sample == 1:
                    dtype = 'i1'
                elif bytes_per_sample == 2:
                    dtype = ('<i2', '>i2')[big_endian]
                else:
                    print('Cannot read', bytes_per_sample, 'byte samples')
                    return
                data = numpy.ndarray(shape=shape, dtype=dtype, buffer=raw_data)
                if swap_axes:
                    # pic pipe data is in (y, c, x) order
                    data = numpy.swapaxes(data, 1, 2)
                if header.precision > 0:
                    data = (data.astype(pt_float)
                            / pt_float(2 ** header.precision))
                if header.comps != 2:
                    # Y & RGB have 128 offset
                    data = data.astype(pt_float) + pt_float(128.0)
                yield data
            
    def read_kw_header(self, pf):
        audit = []
        header = {'data_type': DataTypes.ps_tng_KW, 'precision': 0}
        while True:
            tag1 = pf.read(1)[0]
            if tag1 == 24:
                # two-byte integer value
                tag2 = pf.read(1)[0]
                count = pf.read(1)[0]
                if (tag2, count) == (33, 1):
                    pf.read(2)
                elif (tag2, count) == (34, 2):
                    header['comps'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['interleave'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                elif (tag2, count) == (35, 1):
                    header['chroma_phase'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                elif (tag2, count) == (36, 4):
                    header['full_width'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['full_height'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['field_freq'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['interlace'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                elif (tag2, count) == (37, 4):
                    header['active_width'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['active_height'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['aspect_width'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['aspect_height'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                elif (tag2, count) == (38, 2):
                    header['over_bits'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['acc_bits'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                elif (tag2, count) == (39, 4):
                    header['min_lum'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['max_lum'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['min_chrom'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['max_chrom'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                elif (tag2, count) == (40, 3):
                    header['pos_x'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['pos_y'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['pos_z'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                elif (tag2, count) == (41, 3):
                    header['len_x'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['len_y'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                    header['len_z'] = int.from_bytes(
                        pf.read(2), byteorder='little', signed=True)
                else:
                    print('Unrecognised KW int code', tag2, 'or count', count)
                    pf.read(count * 2)
            elif tag1 == 28:
                # string value
                tag2 = pf.read(1)[0]
                count = pf.read(1)[0]
                if tag2 == 97:
                    audit.append(pf.read(count).decode('ascii'))
                elif tag2 == 98:
                    header['pic_name'] = pf.read(count).decode('ascii')
                elif tag2 == 99:
                    header['code'] = pf.read(count).decode('ascii')
                else:
                    print('Unrecognised KW string code', tag2)
                    pf.read(count)
            elif tag1 == 32:
                # end of header
                break
            else:
                print('Unrecognised KW tag', tag1)
        header['precision'] = ((header['acc_bits'] + 7) // 8) * 8
        header = PicFile(**header)
        return header, audit
