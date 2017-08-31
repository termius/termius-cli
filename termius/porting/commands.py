# -*- coding: utf-8 -*-
"""Module with CLI command to export and import hosts."""
from termius.core.commands.single import RequiredOptions, DetailCommand
from termius.core.storage.strategies import (
    RelatedSaveStrategy, RelatedGetStrategy
)
from termius.porting.providers.securecrt.provider import \
    SecureCRTPortingProvider

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


class ImportHostsCommand(DetailCommand):
    """import hosts from the specified provider"""

    required_options = RequiredOptions(create=('provider', 'source'))
    providers = {
        'securecrt': SecureCRTPortingProvider
    }

    def take_action(self, parsed_args):
        """Process CLI call."""
        self.validate_args(parsed_args, 'create')
        provider_name = parsed_args.provider.lower()
        if provider_name not in self.providers:
            self.log.error('Wrong provider name was specified!')
            return

        provider = self.providers[provider_name](
            source=parsed_args.source, storage=self.storage, crendetial=None
        )
        provider.import_hosts()

        self.log.info('Skipped hosts %i' % len(provider.skipped_hosts))
        self.log.info('SecureCRT hosts has been successfully imported.')

    def get_parser(self, prog_name):
        """Skip detail arguments."""
        return super(DetailCommand, self).get_parser(prog_name)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-p', '--provider',
            metavar='PROVIDER', help='the name of provider (SecureCRT)'
        )
        parser.add_argument(
            '-s', '--source',
            metavar='SOURCE', help='path to source file'
        )

        return parser
