# -*- coding: utf-8 -*-
"""Module to keep operators that using to filter model list."""
from operator import *  # noqa


def rcontains(obj, seq):
    """Act like contains, but takes reverse argument order.

    Motivation: use it like ge, le, gt, lt etc. (aka operator(value, const))
    """
    return contains(seq, obj)
