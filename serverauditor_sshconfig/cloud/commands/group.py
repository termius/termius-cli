# -*- coding: utf-8 -*-
"""Module with Group commands."""
from operator import attrgetter
from ...core.commands import DetailCommand, ListCommand
from ..models import Group
from .ssh_config import SshConfigArgs


class GroupCommand(DetailCommand):
    """Operate with Group object."""

    allowed_operations = DetailCommand.all_operations
    model_class = Group

    def __init__(self, *args, **kwargs):
        """Construct new group command."""
        super(GroupCommand, self).__init__(self, *args, **kwargs)
        self.ssh_config_args = SshConfigArgs()

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(GroupCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for group.'
        )
        parser.add_argument(
            '--ssh', help='Options in ssh_config format.'
        )
        parser.add_argument(
            '-g', '--parent-group',
            metavar='PARENT_GROUP', help="Parent group's id or name."
        )

        self.ssh_config_args.add_agrs(parser)
        return parser

    def create(self, parsed_args):
        """Handle create new instance command."""
        self.create_instance(parsed_args)

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        if instance:
            ssh_config = self.ssh_config_args.serialize_args(
                args, instance.ssh_config
            )
            group = instance
        else:
            group = Group()
            ssh_config = self.ssh_config_args.serialize_args(args, None)

        if args.parent_group:
            raise NotImplementedError('Not implemented')

        group.label = args.label
        group.ssh_config = ssh_config
        return group


class GroupsCommand(ListCommand):
    """Manage group objects."""

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(GroupsCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-r', '--recursive', action='store_true',
            help=('List groups of current group '
                  '(default is current group) recursively.')
        )
        parser.add_argument(
            'group', nargs='?', metavar='GROUP_ID or GROUP_NAME',
            help='List groups in this group.'
        )
        return parser

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        assert False, 'Filtering and recursive not implemented.'
        groups = self.storage.get_all(Group)
        fields = Group.allowed_fields()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in groups]
