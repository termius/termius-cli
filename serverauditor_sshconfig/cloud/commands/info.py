# -*- coding: utf-8 -*-
"""Module with info command."""
import functools
from operator import attrgetter
from cliff.show import ShowOne
from ...core.commands import AbstractCommand
from ...core.commands.mixins import GetRelationMixin
from ...core.storage.strategies import RelatedGetStrategy
from ..models import Group, Host, SshConfig, SshIdentity


class InfoCommand(GetRelationMixin, ShowOne, AbstractCommand):
    """Show info about host or group."""

    get_strategy = RelatedGetStrategy
    model_class = SshConfig

    @property
    def formatter_namespace(self):
        """Return entrypoint with cliff formatters."""
        return 'serverauditor.info.formatters'

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(InfoCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-G', '--group', dest='entry_type',
            action='store_const', const=Group, default=Host,
            help='Show info about group.'
        )
        parser.add_argument(
            '-H', '--host', dest='entry_type',
            action='store_const', const=Host, default=Host,
            help='Show info about host.'
        )
        parser.add_argument(
            '-M', '--no-merge', action='store_true',
            help='Do not merge configs.'
        )
        parser.add_argument(
            '--ssh', action='store_true',
            help='Show info in ssh_config format'
        )
        parser.add_argument('id_or_name', metavar='ID or NAME')
        return parser

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        self.log.info('Info about group or host.')

        instance = self.get_info_instance(parsed_args)
        group_stack = self.get_group_stack(instance)
        full_stack = [instance] + group_stack
        ssh_config = self.merge_ssh_config(full_stack)

        return self.prepare_fields(ssh_config, instance)

    def merge_ssh_config(self, full_stack):
        """Squash full_stack to single ssh_config instance."""
        ssh_config_merger = self.get_ssh_config_merger(full_stack)
        ssh_identity_merger = self.get_ssh_identity_merger(ssh_config_merger)
        ssh_config = ssh_config_merger.merge()
        ssh_config.ssh_identity = ssh_identity_merger.merge()
        return ssh_config

    def get_info_instance(self, args):
        """Retrieve instance from application storage."""
        instance = self.get_relation(args.entry_type, args.id_or_name)
        return instance

    # pylint: disable=no-self-use
    def get_group_stack(self, instance):
        """Generate parent group stack for instance."""
        stack_generator = GroupStackGenerator(instance)
        return stack_generator.generate()

    # pylint: disable=no-self-use
    def get_ssh_config_merger(self, stack):
        """Create ssh config merger for passed stack."""
        return Merger(stack, 'ssh_config', SshConfig())

    # pylint: disable=no-self-use
    def get_ssh_identity_merger(self, ssh_config_merger):
        """Create ssh_identity merger for passed merger."""
        stack = [
            i for i in ssh_config_merger.get_entry_stack()
            if not i.ssh_identity.is_visible
        ]
        return Merger(stack, 'ssh_identity', SshIdentity())

    # pylint: disable=no-self-use
    def prepare_fields(self, ssh_config, instance):
        """Generate 2size tuple with ssh_config fields.

        Warning there is one additional field - 'address'.
        """
        ssh_config_fields = ssh_config.allowed_fields()
        keys = tuple(ssh_config_fields) + ('address',)
        values = (
            attrgetter(*ssh_config_fields)(ssh_config) +
            (getattr(instance, 'address', ''),)
        )
        return (keys, values)


class GroupStackGenerator(object):
    """Class to keep parent group stack generation."""

    group_getter = attrgetter('parent_group')

    def __init__(self, instance):
        """Construct new generator instance."""
        if isinstance(instance, Host):
            self.root_group = instance.group
        else:
            self.root_group = instance.parent_group
        self.instance = instance

    def generate(self):
        """Generate list (aka stack) of parent groups."""
        return list(self.iterate_groups())

    def iterate_groups(self):
        """Iterator over instances parent groups."""
        group = self.root_group
        while group:
            yield group
            group = self.group_getter(group)


class Merger(object):
    """Class to process ssh config merging."""

    def __init__(self, stack, stack_field, initial):
        """Construct new instance stack."""
        self.stack = stack
        self.stack_field = stack_field
        self.merge_field_list = initial.mergable_fields
        self.stack_field_getter = attrgetter(stack_field)
        self.initial = initial

    def get_entry_stack(self):
        """Generate entries stack from parent stack."""
        not_filtered = [self.stack_field_getter(i) for i in self.stack]
        return [i for i in not_filtered if i]

    def merge(self):
        """Merge instances of full_stack to single instance."""
        entries = self.get_entry_stack()
        merged = functools.reduce(self.reducer, entries, self.initial)
        return merged

    def reducer(self, accumulator, value):
        """Merge value fields to accumulator."""
        for i in self.merge_field_list:
            merge_field(accumulator, value, i)
        return accumulator


def merge_field(left, right, field):
    """Merge field of right instance to left one."""
    left_field = getattr(left, field)
    if not left_field:
        setattr(left, field, getattr(right, field))
