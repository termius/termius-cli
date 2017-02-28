#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entrypoint for CLI tool."""
import sys
from termius.app import TermiusApp


def main(argv=sys.argv[1:]):
    """Process call from terminal."""
    app = TermiusApp()

    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
