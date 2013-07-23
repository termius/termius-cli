# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY2:
    p_input = raw_input
    p_map = map

    def to_bytes(s):
        if isinstance(s, str):
            return s
        if isinstance(s, unicode):
            return s.encode('utf-8')

    to_str = to_bytes

    def bchr(s):
        return chr(s)

    def bord(s):
        return ord(s)

elif PY3:
    p_input = input
    p_map = lambda f, it: list(map(f, it))

    def to_bytes(s):
        if isinstance(s, bytes):
            return s
        if isinstance(s, str):
            return s.encode('utf-8')

    def to_str(s):
        if isinstance(s, bytes):
            return s.decode('utf-8')
        if isinstance(s, str):
            return s

    def bchr(s):
        return bytes([s])

    def bord(s):
        return s
