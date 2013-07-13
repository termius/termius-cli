# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

import sys
from multiprocessing import Pipe, Process


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def parallel_map(f, iterable):

    def spawn(f):
        def fun(pipe, x):
            pipe.send(f(x))
            pipe.close()
        return fun

    pipes = [Pipe() for _ in range(len(iterable))]
    processes = [Process(target=spawn(f), args=(c, x)) for x, (p, c) in zip(iterable, pipes)]
    [p.start() for p in processes]
    [p.join() for p in processes]
    return [p.recv() for (p, c) in pipes]


# now parallel_map isn't needed
parallel_map = lambda f, it: list(map(f, it))


if PY2:
    p_input = raw_input

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
