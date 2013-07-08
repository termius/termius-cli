# coding: utf-8

"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""

from itertools import izip
from multiprocessing import Pipe, Process


def parallel_map(f, iterable):

    def spawn(f):
        def fun(pipe, x):
            pipe.send(f(x))
            pipe.close()
        return fun

    pipes = [Pipe() for _ in xrange(len(iterable))]
    processes = [Process(target=spawn(f), args=(c, x)) for x, (p, c) in izip(iterable, pipes)]
    [p.start() for p in processes]
    [p.join() for p in processes]
    return [p.recv() for (p, c) in pipes]
