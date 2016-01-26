# coding: utf-8

import os


def expand_and_format_path(paths, **kwargs):
    return [os.path.expanduser(i.format(**kwargs)) for i in paths]
