# -*- coding: utf-8 -*-
"""Module for connect command."""
import subprocess
from ..account.managers import AccountManager
from ..core.commands import AbstractCommand
from ..core.commands.mixins import GetRelationMixin, SshConfigMergerMixin
from ..core.models.terminal import Host, PFRule
from ..core.storage.strategies import RelatedGetStrategy
from ..formatters.mixins import SshCommandFormatterMixin


class ConnectCommand(SshCommandFormatterMixin, SshConfigMergerMixin,
                     GetRelationMixin, AbstractCommand):
    """connect to a specific host with NAME or ID"""

    get_strategy = RelatedGetStrategy

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-H', '--host', const=Host,
            dest='model', action='store_const', default=Host,
            help='connect to a host'
        )
        parser.add_argument(
            '-R', '--pfrule', const=PFRule,
            dest='model', action='store_const', default=Host,
            help='connect to a host using a port forwarding rule'
        )
        parser.add_argument(
            'entry', metavar='ID or NAME',
            help='connect to the specific host'
        )
        return parser

    def take_action(self, parsed_args):
        """Process CLI call."""
        instance = self.get_instance(parsed_args)
        host = instance.host if instance.host else instance
        ssh_config = self.get_merged_ssh_config(host)
        self.call_ssh_command(ssh_config, host, instance)
        return

    def call_ssh_command(self, ssh_config, host, instance):
        """Call ssh command to connect to host."""
        pfrule = isinstance(instance, PFRule) and instance or None
        command = self.ssh_config_to_command(ssh_config, host.address, pfrule)
        subprocess.call(command, shell=True)

    def ssh_config_to_command(self, config, address, pfrule):
        """Generate ssh command string with arguments from config."""
        ssh_key = config.get_ssh_key()
        ssh_key_path = ssh_key and ssh_key.file_path(self)
        config['agent_forwarding'] = (
            AccountManager(self.config).get_settings().get('agent_forwarding')
        )
        return self.render_command(
            config, address,
            ssh_key_path, pfrule=pfrule
        )

    def get_instance(self, args):
        """Retrieve instance from storage."""
        return self.get_relation(args.model, args.entry)
