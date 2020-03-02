#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entrypoint for CLI tool."""
import sys
from termius.app import TermiusApp


def main(argv=None):
    """Process call from terminal."""
    app = TermiusApp()

    return app.run(argv or sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
