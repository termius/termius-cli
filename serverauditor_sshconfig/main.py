#!/usr/bin/env python
# coding: utf-8

import sys
from serverauditor_sshconfig.app import ServerauditorApp


def main(argv=sys.argv[1:]):
    app = ServerauditorApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
