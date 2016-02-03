# -*- coding: utf-8 -*-
"""Module for connect command."""
import subprocess
from ..core.commands import AbstractCommand
from ..core.commands.mixins import GetRelationMixin, SshConfigMergerMixin
from ..core.models.terminal import Host
from ..core.storage.strategies import RelatedGetStrategy
from ..formatters.mixins import SshCommandFormatterMixin


class ConnectCommand(SshCommandFormatterMixin, SshConfigMergerMixin,
                     GetRelationMixin, AbstractCommand):
    """Connect to specific host."""

    get_strategy = RelatedGetStrategy

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(ConnectCommand, self).get_parser(prog_name)
        parser.add_argument(
            'host', metavar='HOST_ID or HOST_NAME',
            help='Connect to this host.'
        )
        return parser

    def take_action(self, parsed_args):
        """Process CLI call."""
        instance = self.get_relation(Host, parsed_args.host)
        ssh_config = self.get_merged_ssh_config(instance)
        self.call_ssh_command(ssh_config, instance)
        return

    def call_ssh_command(self, ssh_config, host):
        """Call ssh command to connect to host."""
        ssh_command = self.ssh_config_to_command(ssh_config, host.address)
        subprocess.call(ssh_command, shell=True)

    def ssh_config_to_command(self, config, address):
        """Generate ssh command string with arguments from config."""
        return self.render_command(config, address)
