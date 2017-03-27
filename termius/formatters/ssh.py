# -*- coding: utf-8 -*-
"""Module with cliff single formatter into ssh command."""
from cliff.formatters.base import SingleFormatter
from .mixins import SshCommandFormatterMixin


class SshFormatter(SshCommandFormatterMixin, SingleFormatter):
    """Cliff formatter for ssh config into ssh command."""

    def add_argument_group(self, parser):
        """Add ssh formatter's options to arg parser."""
        group = parser.add_argument_group(
            title='formatter to ssh command',
            description='a format a ssh command with arguments',
        )
        group.add_argument(
            '--address',
            action='store',
            help='use passed address for ssh command',
        )

    def emit_one(self, column_names, data, stdout, parsed_args):
        """Generate ssh config command."""
        ssh_config = dict(zip(column_names, data))
        address = parsed_args.address or ssh_config['address']
        ssh_key_path = ssh_config.get('ssh_key_path')
        stdout.write(self.render_command(ssh_config, address, ssh_key_path))
        return
