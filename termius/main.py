#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entrypoint for CLI tool."""
import sys
import os
import warnings
from termius.app import TermiusApp


if os.getenv('TERMIUS_CLI_DEBUG'):
    warnings.filterwarnings(
        'ignore', r'Python 2 is no longer supported by the Python core team. ',
        UserWarning, r'termius'
    )


def main(argv=None):
    """Process call from terminal."""
    app = TermiusApp()

    return app.run(argv or sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
