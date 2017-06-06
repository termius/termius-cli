# -*- coding: utf-8 -*-
"""Module with info command."""
from operator import attrgetter
from cliff.show import ShowOne

from ..account.managers import AccountManager
from ..core.commands import AbstractCommand
from ..core.commands.mixins import GetRelationMixin, SshConfigMergerMixin
from ..core.storage.strategies import RelatedGetStrategy
from ..core.models.terminal import Group, Host, SshConfig


class InfoCommand(SshConfigMergerMixin, GetRelationMixin,
                  ShowOne, AbstractCommand):
    """display info about a host or group"""

    get_strategy = RelatedGetStrategy
    model_class = SshConfig

    @property
    def formatter_namespace(self):
        """Return entrypoint with cliff formatters."""
        return 'termius.info.formatters'

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-G', '--group', dest='entry_type',
            action='store_const', const=Group, default=Host,
            help='show info about group'
        )
        parser.add_argument(
            '-H', '--host', dest='entry_type',
            action='store_const', const=Host, default=Host,
            help='show info about host'
        )
        parser.add_argument(
            '-M', '--no-merge', action='store_true',
            help='do not merge configs'
        )
        parser.add_argument(
            'id_or_name',
            metavar='ID or NAME',
            help='display information about the group or host with ID'
        )
        return parser

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        instance = self.get_relation(
            parsed_args.entry_type, parsed_args.id_or_name
        )
        ssh_config = self.get_merged_ssh_config(instance)

        return self.prepare_fields(ssh_config, instance)

    def prepare_fields(self, ssh_config, instance):
        """Generate 2size tuple with ssh_config fields.

        Warning there is one additional field - 'address'.
        """
        ssh_config_fields = tuple(ssh_config.allowed_fields())
        additional_fields = ('address', 'ssh_key_path', 'agent_forwarding')
        keys = ssh_config_fields + additional_fields
        ssh_key = ssh_config.get_ssh_key()
        agent_forwarding = (
            AccountManager(self.config).get_settings()
            .get('agent_forwarding')
        )
        values = (
            attrgetter(*ssh_config_fields)(ssh_config) +
            (
                getattr(instance, 'address', ''),
                ssh_key and ssh_key.file_path(self),
                agent_forwarding,
            )
        )
        return (keys, values)
