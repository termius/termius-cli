# -*- coding: utf-8 -*-
"""Module with Group commands."""
import functools
from ..core.commands import DetailCommand, ListCommand
from ..core.commands.mixins import GroupStackGetterMixin
from ..core.models.terminal import Group
from ..core.exceptions import InvalidArgumentException
from .ssh_config import SshConfigArgs


class GroupCommand(GroupStackGetterMixin, DetailCommand):
    """Operate with Group object."""

    model_class = Group

    def __init__(self, *args, **kwargs):
        """Construct new group command."""
        super(GroupCommand, self).__init__(*args, **kwargs)
        self.ssh_config_args = SshConfigArgs(self)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-g', '--parent-group',
            metavar='PARENT_GROUP', help="Parent group's id or name."
        )

        self.ssh_config_args.add_agrs(parser)
        return parser

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
        self.validate_parent_group(group)
        return group

    def validate_parent_group(self, group):
        """Raise an error when group have cyclic folding."""
        group_id = group.id
        if not group_id:
            return
        group_stack = self.get_group_stack(group)
        not_unique = any([i.id for i in group_stack if i.id == group_id])
        if not_unique:
            raise InvalidArgumentException('Cyclic group founded!')


class GroupsCommand(ListCommand):
    """Manage group objects."""

    model_class = Group

    def extend_parser(self, parser):
        """Add more arguments to parser."""
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
        return functools.reduce(self._collect_subgroup, top_groups, [])

    def _collect_subgroup(self, accumulator, group):
        children = self.get_groups(group.id)
        return accumulator + [group] + self.collect_group_recursivle(children)
