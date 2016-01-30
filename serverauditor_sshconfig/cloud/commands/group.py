# -*- coding: utf-8 -*-
"""Module with Group commands."""
from ...core.commands import DetailCommand, ListCommand
from ..models import Group
from .ssh_config import SshConfigArgs


class GroupCommand(DetailCommand):
    """Operate with Group object."""

    allowed_operations = DetailCommand.all_operations
    model_class = Group

    def __init__(self, *args, **kwargs):
        """Construct new group command."""
        super(GroupCommand, self).__init__(*args, **kwargs)
        self.ssh_config_args = SshConfigArgs(self)

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

        group.label = args.label
        group.ssh_config = ssh_config
        if args.parent_group:
            group.parent_group = self.get_relation(Group, args.parent_group)
        return group


class GroupsCommand(ListCommand):
    """Manage group objects."""

    model_class = Group

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
        parent_group_id = self.get_parent_group_id(parsed_args)
        groups = self.get_groups(parent_group_id)
        if parsed_args.recursive:
            groups = self.collect_group_recursivle(groups)
        return self.prepare_result(groups)

    def get_groups(self, group_id):
        """Retrieve all child groups of passed group."""
        return self.storage.filter(
            Group, **{'parent_group': group_id}
        )

    def get_parent_group_id(self, args):
        """Return parent group id  or None from command line arguments."""
        return args.group and self.get_relation(Group, args.group).id

    def collect_group_recursivle(self, top_groups):
        """Return all child groups of top_groups."""
        return reduce(self._collect_subgroup, top_groups, [])

    def _collect_subgroup(self, accumulator, group):
        children = self.get_groups(group.id)
        return accumulator + [group] + self.collect_group_recursivle(children)
