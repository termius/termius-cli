# -*- coding: utf-8 -*-
"""Module keeps command arguments converters."""


def boolean_yes_no(string):
    """Convert `"yes"`, `"no"` to boolean `True`, `False`."""
    return string == 'yes'
