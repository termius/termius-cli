
# pylint: disable=unused-import
from operator import (
    eq, ne, gt, lt, le, ge, contains
)


def rcontains(obj, seq):
    return contains(seq, obj)
