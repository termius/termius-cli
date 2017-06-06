# -*- coding: utf-8 -*-
"""Module with CLI command to export and import hosts."""
from termius.core.storage.strategies import (
    RelatedSaveStrategy, RelatedGetStrategy
)

from termius.porting.providers.ssh.provider import SSHPortingProvider

from ..core.commands import AbstractCommand


class SSHImportCommand(AbstractCommand):
    """import the local ssh config file"""

    save_strategy = RelatedSaveStrategy
    get_strategy = RelatedGetStrategy

    def take_action(self, parsed_args):
        """Process CLI call."""
        provider = SSHPortingProvider(storage=self.storage, crendetial=None)
        provider.import_hosts()

        if len(provider.skipped_hosts):
            for alias in provider.skipped_hosts:
                self.log.info(
                    'Host %s already exists, skip...' % alias
                )

            self.log.info(
                '\nImport completed, part of the hosts was ignored'
            )
        else:
            self.log.info(
                'Import hosts from ~/.ssh/config to local storage'
            )


class SSHExportCommand(AbstractCommand):
    """export hosts from the local storage to a file"""

    get_strategy = RelatedGetStrategy

    def take_action(self, parsed_args):
        """Process CLI call."""
        provider = SSHPortingProvider(storage=self.storage, crendetial=None)
        provider.export_hosts()

        self.log.info(
            'Export hosts from local storage to ~/.termius/sshconfig'
        )
