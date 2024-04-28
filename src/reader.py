from os import read
import struct
from pygame.math import Vector2 as vec2
from data_types import *


class WADReader:
    def __init__(self, path):
        self.wad_file = open(path, 'rb')
        self.header = self.read_header()
        self.directory = self.read_directory()

    def read_header(self):
        return {
            'wad_type': self.read_string(offset=0, num_bytes=4),
            'lump_count': self.read_4_bytes(offset=4),
            'init_offset': self.read_4_bytes(offset=8)
        }

    def read_directory(self):
        dir = []
        for i in range(self.header['lump_count']):
            offset = self.header['init_offset'] + i * 16
            lump_info = {
                'lump_offset': self.read_4_bytes(offset),
                'lump_size': self.read_4_bytes(offset + 4),
                'lump_name': self.read_string(offset + 8, num_bytes=8)
            }
            dir.append(lump_info)
        return dir

    def read_linedef(self, offset):
        # 14 bytes - 2H x 7
        read_2_bytes = self.read_2_bytes

        linedef = Linedef()
        linedef.start_vertex_id = read_2_bytes(offset, byte_format='H')
        linedef.end_vertex_id = read_2_bytes(offset + 2, byte_format='H')
        linedef.flags = read_2_bytes(offset + 4, byte_format='H')
        linedef.line_type = read_2_bytes(offset + 6, byte_format='H')
        linedef.sector_tag = read_2_bytes(offset + 8, byte_format='H')
        linedef.front_sidedef_id = read_2_bytes(offset + 10, byte_format='H')
        linedef.back_sidedef_id = read_2_bytes(offset + 12, byte_format='H')
        return linedef

    def read_vertex(self, offset):
        # 4 bytes = 2h + 2h
        x = self.read_2_bytes(offset, byte_format='h')
        y = self.read_2_bytes(offset + 2, byte_format='h')
        return vec2(x, y)

    def read_node(self, offset):
        # 28 bytes = 2h x 12 + 2H x 2
        read_2_bytes = self.read_2_bytes

        node = Node()
        node.x_partition = read_2_bytes(offset, byte_format='h')
        node.y_partition = read_2_bytes(offset + 2, byte_format='h')
        node.dx_partition = read_2_bytes(offset + 4, byte_format='h')
        node.dy_partition = read_2_bytes(offset + 6, byte_format='h')

        node.bbox['front'].top = read_2_bytes(offset + 8, byte_format='h')
        node.bbox['front'].bottom = read_2_bytes(offset + 10, byte_format='h')
        node.bbox['front'].left = read_2_bytes(offset + 12, byte_format='h')
        node.bbox['front'].right = read_2_bytes(offset + 14, byte_format='h')

        node.bbox['back'].top = read_2_bytes(offset + 16, byte_format='h')
        node.bbox['back'].bottom = read_2_bytes(offset + 18, byte_format='h')
        node.bbox['back'].left = read_2_bytes(offset + 20, byte_format='h')
        node.bbox['back'].right = read_2_bytes(offset + 22, byte_format='h')

        node.front_child_id = read_2_bytes(offset + 24, byte_format='H')
        node.back_child_id = read_2_bytes(offset + 26, byte_format='H')
        return node

    def read_sub_sector(self, offset):
        # 4 bytes = 2h + 2h
        read_2_bytes = self.read_2_bytes

        sub_sector = SubSector()
        sub_sector.seg_count = read_2_bytes(offset, byte_format='h')
        sub_sector.first_seg_id = read_2_bytes(offset + 2, byte_format='h')
        return sub_sector

    def read_segment(self, offset):
        # 12 bytes = 2h x 6
        read_2_bytes = self.read_2_bytes

        seg = Seg()
        seg.start_vertex_id = read_2_bytes(offset, byte_format='h')
        seg.end_vertex_id = read_2_bytes(offset + 2, byte_format='h')
        seg.angle = read_2_bytes(offset + 4, byte_format='h')
        seg.linedef_id = read_2_bytes(offset + 6, byte_format='h')
        seg.direction = read_2_bytes(offset + 8, byte_format='h')
        seg.offset = read_2_bytes(offset + 10, byte_format='h')
        return seg

    def read_thing(self, offset):
        # 10 bytes = 2h + 2h + 2H x 3
        read_2_bytes = self.read_2_bytes

        thing = Thing()
        x = read_2_bytes(offset, byte_format='h')
        y = read_2_bytes(offset + 2, byte_format='h')
        thing.angle = read_2_bytes(offset + 4, byte_format='H')
        thing.type = read_2_bytes(offset + 6, byte_format='H')
        thing.flags = read_2_bytes(offset + 8, byte_format='H')
        thing.pos = vec2(x, y)
        return thing

    def read_sector(self, offset):
        # 26 bytes = 2h + 2h + 8c + 8c + 2H x 3
        read_2_bytes = self.read_2_bytes
        read_string = self.read_string
        
        sector = Sector()
        sector.floor_height = read_2_bytes(offset, byte_format='h')
        sector.ceil_height = read_2_bytes(offset + 2, byte_format='h')
        sector.floor_texture = read_string(offset + 4, num_bytes=8)
        sector.ceil_texture = read_string(offset + 12, num_bytes=8)
        sector.light_level = read_2_bytes(offset + 20, byte_format='H')
        sector.type = read_2_bytes(offset + 22, byte_format='H')
        sector.tag = read_2_bytes(offset + 24, byte_format='H')
        return sector

    def read_sidedef(self, offset):
        # 30 bytes = 2h + 2h + 8c + 8c + 8c + 2H
        read_2_bytes = self.read_2_bytes
        read_string = self.read_string

        sidedef = Sidedef()
        sidedef.x_offset = read_2_bytes(offset, byte_format='h')
        sidedef.y_offset = read_2_bytes(offset + 2, byte_format='h')
        sidedef.upper_texture = read_string(offset + 4, num_bytes=8)
        sidedef.lower_texture = read_string(offset + 12, num_bytes=8)
        sidedef.middle_texture = read_string(offset + 20, num_bytes=8)
        sidedef.sector_id = read_2_bytes(offset + 28, byte_format='H')
        return sidedef

    # Helper Functions
    def read_1_byte(self, offset, byte_format='B'):
        # B - unsigned char, b - signed char
        return self.read_bytes(offset=offset, num_bytes=1, byte_format=byte_format)[0]

    def read_2_bytes(self, offset, byte_format):
        # H - uint16, h - int16
        return self.read_bytes(offset=offset, num_bytes=2, byte_format=byte_format)[0]

    def read_4_bytes(self, offset, byte_format='i'):
        # i - int32
        return self.read_bytes(offset=offset, num_bytes=4, byte_format=byte_format)[0]

    def read_string(self, offset, num_bytes):
        # c - char
        return ''.join(b.decode('ascii') for b in
                       self.read_bytes(offset, num_bytes,
                                       byte_format='c' * num_bytes)
                       if ord(b) != 0).upper()

    def read_bytes(self, offset, num_bytes, byte_format):
        self.wad_file.seek(offset)
        buffer = self.wad_file.read(num_bytes)
        return struct.unpack(byte_format, buffer)

    def close(self):
        self.wad_file.close()
