# -*- coding: utf-8 -*-
"""Module with Host commands."""
from ...core.exceptions import ArgumentRequiredException
from ...core.commands import DetailCommand, ListCommand
from ..models import Host, Group
from .ssh_config import SshConfigArgs


class HostCommand(DetailCommand):
    """Operate with Host object."""

    allowed_operations = DetailCommand.all_operations
    model_class = Host

    def __init__(self, *args, **kwargs):
        """Construct new host command."""
        super(HostCommand, self).__init__(*args, **kwargs)
        self.ssh_config_args = SshConfigArgs(self)

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(HostCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for host.'
        )
        parser.add_argument(
            '--ssh', metavar='SSH_CONFIG_OPTIONS',
            help='Options in ssh_config format.'
        )
        parser.add_argument(
            '-t', '--tags', metavar='TAG_LIST',
            help='Comma separated tag list for host, e.g. "web,django".'
        )
        parser.add_argument(
            '-g', '--group', metavar='GROUP_ID or GROUP_NAME',
            help='Move hosts to this group.'
        )
        parser.add_argument(
            '-a', '--address',
            metavar='ADDRESS', help='Address of host.'
        )

        self.ssh_config_args.add_agrs(parser)
        return parser

    def create(self, parsed_args):
        """Handle create new instance command."""
        if not parsed_args.address:
            raise ArgumentRequiredException('Address is required.')

        self.create_instance(parsed_args)

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        if instance:
            ssh_config = self.ssh_config_args.serialize_args(
                args, instance.ssh_config
            )
            host = instance
        else:
            host = Host()
            ssh_config = self.ssh_config_args.serialize_args(args, None)

        host.label = args.label
        host.address = args.address
        host.ssh_config = ssh_config
        if args.group:
            host.group = self.get_relation(Group, args.group)
        return host


class HostsCommand(ListCommand):
    """Manage host objects."""

    model_class = Host

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(HostsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-t', '--tags', metavar='TAG_LIST',
            help=('(Comma separated tag list) list hosts with such tags.')
        )
        parser.add_argument(
            '-g', '--group', metavar='GROUP_ID or GROUP_NAME',
            help=('List hosts in group (default is current group).')
        )
        return parser

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        assert False, 'Filtering by tags not implemented.'
        group_id = self.get_group_id(parsed_args)
        hosts = self.get_hosts(group_id)
        return self.prepare_result(hosts)

    def get_hosts(self, group_id):
        return self.storage.filter(Host, **{'group': group_id})

    def get_group_id(self, args):
        return args.group and self.get_relation(Group, args.group).id
