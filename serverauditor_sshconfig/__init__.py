# -*- coding: utf-8 -*-
"""Package with CLI tool and API."""
__version__ = (0, 7, 2)


def get_version():
    """Return current version."""
    return '.'.join([str(i) for i in __version__])
