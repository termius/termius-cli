# -*- coding: utf-8 -*-
"""Miscellaneous extra functions."""
import os


def expand_and_format_path(paths, **kwargs):
    """Format and expand filename list."""
    return [os.path.expanduser(i.format(**kwargs)) for i in paths]
