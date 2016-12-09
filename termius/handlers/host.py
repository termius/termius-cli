# -*- coding: utf-8 -*-
"""Module with Host commands."""
from operator import attrgetter
from cached_property import cached_property
from ..core.commands import DetailCommand, ListCommand
from ..core.commands.single import RequiredOptions
from ..core.commands.mixins import SshConfigPrepareMixin
from ..core.storage.strategies import RelatedGetStrategy
from ..core.models.terminal import Host, Group, TagHost
from .taghost import TagListArgs
from .ssh_config import SshConfigArgs


class HostCommand(DetailCommand):
    """Operate with Host object."""

    model_class = Host
    required_options = RequiredOptions(create=('address',))

    @cached_property
    def fields(self):
        """Return dictionary of args serializers to models field."""
        _fields = {
            i: attrgetter(i) for i in ('label', 'address')
        }
        _fields['group'] = self.get_safely_instance_partial(Group, 'group')
        return _fields

    def __init__(self, *args, **kwargs):
        """Construct new host command."""
        super(HostCommand, self).__init__(*args, **kwargs)
        self.ssh_config_args = SshConfigArgs(self)
        self.taglist_args = TagListArgs(self)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-t', '--tag', metavar='TAG_NAME',
            action='append', default=[], dest='tags',
            help='Specify the tag(s) for host, can be repeated'
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

    def update_children(self, instance, args):
        """Create new model entry."""
        if args.tags is not None:
            self.update_tag_list(instance, args.tags)

    def update_tag_list(self, host, tags):
        """Update tag list for host instance."""
        tag_instanes = self.taglist_args.get_or_create_tag_instances(tags)
        self.taglist_args.update_taghosts(host, tag_instanes)

    def pre_save(self, instance):
        """Patch instance fields before saving."""
        instance.update_interaction_date()

    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        instance = super(HostCommand, self).serialize_args(args, instance)
        ssh_config = instance.get_assign_ssh_config()
        instance.ssh_config = self.ssh_config_args.serialize_args(
            args, ssh_config
        )
        return instance


class HostsCommand(SshConfigPrepareMixin, ListCommand):
    """Manage host objects."""

    model_class = Host
    get_strategy = RelatedGetStrategy

    def __init__(self, *args, **kwargs):
        """Construct new hosts command."""
        super(HostsCommand, self).__init__(*args, **kwargs)
        self.taglist_args = TagListArgs(self)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-t', '--tag', metavar='TAG_NAME',
            action='append', default=[], dest='tags',
            help=('Specify the tag(s) for host, can be repeated')
        )
        parser.add_argument(
            '-g', '--group', metavar='GROUP_ID or GROUP_NAME',
            help=('List hosts in group (default is current group).')
        )
        return parser

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        group_id = self.get_group_id(parsed_args)
        hosts = self.get_hosts(group_id)
        if parsed_args.tags:
            hosts = self.filter_host_by_tags(hosts, parsed_args.tags)
        return self.prepare_result(hosts)

    def get_hosts(self, group_id):
        """Get host list by group id."""
        if group_id:
            return self.storage.filter(Host, **{'group.id': group_id})
        else:
            return self.storage.filter(Host, **{'group': None})

    def get_group_id(self, args):
        """Get group id by group id or label."""
        return args.group and self.get_relation(Group, args.group).id

    def filter_host_by_tags(self, hosts, tags):
        """Filter host list by tag csv list."""
        tags = self.taglist_args.get_tag_instances(tags)
        tag_ids = [i.id for i in tags]
        host_ids = [i.id for i in hosts]
        taghost_instances = self.storage.filter(TagHost, all, **{
            'tag.id.rcontains': tag_ids
        })
        filtered_host_ids = {i.host.id for i in taghost_instances}
        intersected_host_ids = set(host_ids) & filtered_host_ids
        return self.storage.filter(
            Host, **{'id.rcontains': intersected_host_ids}
        )
