#!/usr/bin/env python
#
# Copyright 2013 Crystalnix

import sys

from core.application import SSHConfigApplication
from core.api import API
from core.cryptor import RNCryptor
from core.logger import PrettyLogger
from core.ssh_config import SSHConfig


class ImportSSHConfigApplication(SSHConfigApplication):

    def run(self):
        self._greeting()

        self._get_sa_user()
        self._get_sa_keys_and_connections()
        self._decrypt_sa_keys_and_connections()

        self._parse_local_config()
        self._sync_for_import()
        self._choose_new_hosts()
        self._create_keys_and_connections()

        self._valediction()
        return

    def _greeting(self):
        self._logger.log("ServerAuditor's ssh config script. Import from SA servers to local machine.", color='magenta')
        return

    def _sync_for_import(self):
        pass

    def _choose_new_hosts(self):
        pass

    def _create_keys_and_connections(self):
        pass


def main():
    app = ImportSSHConfigApplication(api=API(), ssh_config=SSHConfig(), cryptor=RNCryptor(), logger=PrettyLogger())
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        pass
    return


if __name__ == "__main__":

    main()