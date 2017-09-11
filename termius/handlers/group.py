# -*- coding: utf-8 -*-
"""Module with Group commands."""
import functools
from operator import attrgetter
from cached_property import cached_property
from ..core.commands import DetailCommand, ListCommand
from ..core.commands.mixins import GroupStackGetterMixin
from ..core.models.terminal import Group
from ..core.commands.single import RequiredOptions
from ..core.storage.strategies import RelatedGetStrategy
from ..core.exceptions import InvalidArgumentException
from .ssh_config import SshConfigArgs


class GroupCommand(GroupStackGetterMixin, DetailCommand):
    """work with a group"""

    model_class = Group
    required_options = RequiredOptions(create=('label',))

    @cached_property
    def fields(self):
        """Return dictionary of args serializers to models field."""
        _fields = {
            i: attrgetter(i) for i in ('label', )
        }

        _fields['parent_group'] = self.get_safely_instance_partial(
            Group, 'parent_group'
        )
        return _fields

    def __init__(self, app, app_args, cmd_name=None):
        """Construct new group command."""
        super(GroupCommand, self).__init__(app, app_args, cmd_name)
        self.ssh_config_args = SshConfigArgs(self)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-g', '--parent-group',
            metavar='PARENT_GROUP',
            help='select the parent group with ID or NAME'
        )
        self.ssh_config_args.add_agrs(parser)
        return parser

    def validate(self, group):
        """Raise an error when group have cyclic folding."""
        group_id = group.id
        if not group_id:
            return
        group_stack = self.get_group_stack(group)
        not_unique = any([i.id for i in group_stack if i.id == group_id])
        if not_unique:
            raise InvalidArgumentException('Cyclic group founded!')

    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        instance = super(GroupCommand, self).serialize_args(args, instance)
        ssh_config = instance.get_assign_ssh_config()
        instance.ssh_config = self.ssh_config_args.serialize_args(
            args, ssh_config
        )
        return instance


class GroupsCommand(ListCommand):
    """list all groups"""

    model_class = Group
    get_strategy = RelatedGetStrategy

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-r', '--recursive', action='store_true',
            help=('list groups of current group '
                  '(default is current group) recursively.')
        )
        parser.add_argument(
            'group', nargs='?', metavar='GROUP_ID or GROUP_NAME',
            help='list groups in the group with ID or NAME'
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
        if group_id:
            filter_operation = {'parent_group.id': group_id}
        else:
            filter_operation = {'parent_group': None}
        return self.storage.filter(Group, **filter_operation)

    def get_parent_group_id(self, args):
        """Return parent group id  or None from command line arguments."""
        return args.group and self.get_relation(Group, args.group).id

    def collect_group_recursivle(self, top_groups):
        """Return all child groups of top_groups."""
        return functools.reduce(self._collect_subgroup, top_groups, [])

    def _collect_subgroup(self, accumulator, group):
        children = self.get_groups(group.id)
        return accumulator + [group] + self.collect_group_recursivle(children)
