# -*- coding: utf-8 -*-
"""Module with CLI command to export and import hosts."""
from termius.core.storage.strategies import (
    RelatedSaveStrategy, RelatedGetStrategy
)

from termius.porting.providers.ssh.provider import SSHPortingProvider

from ..core.commands import AbstractCommand


class SSHImportCommand(AbstractCommand):
    """Import hosts from user`s ssh config."""

    save_strategy = RelatedSaveStrategy
    get_strategy = RelatedGetStrategy

    def take_action(self, parsed_args):
        """Process CLI call."""
        provider = SSHPortingProvider(storage=self.storage, crendetial=None)
        provider.import_hosts()

        self.log.info('Import hosts from ~/.ssh/config to local storage.')


class SSHExportCommand(AbstractCommand):
    """Export hosts from local storage to generated file."""

    get_strategy = RelatedGetStrategy

    def take_action(self, parsed_args):
        """Process CLI call."""
        provider = SSHPortingProvider(storage=self.storage, crendetial=None)
        provider.export_hosts()

        self.log.info(
            'Export hosts from local storage to ~/.termius/sshconfig'
        )
