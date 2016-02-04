# -*- coding: utf-8 -*-
"""Module with Host commands."""
from ..core.commands import DetailCommand, ListCommand
from ..core.commands.single import RequiredOptions
from ..core.models.terminal import Host, Group, TagHost
from .taghost import TagListArgs
from .ssh_config import SshConfigArgs


class HostCommand(DetailCommand):
    """Operate with Host object."""

    model_class = Host
    required_options = RequiredOptions(create=('address',))

    def __init__(self, *args, **kwargs):
        """Construct new host command."""
        super(HostCommand, self).__init__(*args, **kwargs)
        self.ssh_config_args = SshConfigArgs(self)
        self.taglist_args = TagListArgs(self)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
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

    def update_children(self, instance, args):
        """Create new model entry."""
        if args.tags is not None:
            self.update_tag_list(instance, args.tags)

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

    def update_tag_list(self, host, tag_csv):
        """Update tag list for host instance."""
        tag_instanes = self.taglist_args.get_or_create_tag_instances(tag_csv)
        self.taglist_args.update_taghosts(host, tag_instanes)


class HostsCommand(ListCommand):
    """Manage host objects."""

    model_class = Host

    def __init__(self, *args, **kwargs):
        """Construct new hosts command."""
        super(HostsCommand, self).__init__(*args, **kwargs)
        self.taglist_args = TagListArgs(self)

    def extend_parser(self, parser):
        """Add more arguments to parser."""
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
        group_id = self.get_group_id(parsed_args)
        hosts = self.get_hosts(group_id)
        filtered_hosts = self.filter_host_by_tags(hosts, parsed_args)
        return self.prepare_result(filtered_hosts)

    def get_hosts(self, group_id):
        """Get host list by group id."""
        return self.storage.filter(Host, **{'group': group_id})

    def get_group_id(self, args):
        """Get group id by group id or label."""
        return args.group and self.get_relation(Group, args.group).id

    def filter_host_by_tags(self, hosts, args):
        """Filter host list by tag csv list."""
        if args.tags:
            tags = self.taglist_args.get_tag_instances(args.tags)
            tag_ids = [i.id for i in tags]
            host_ids = [i.id for i in hosts]
            taghost_instances = self.storage.filter(TagHost, all, **{
                'tag.rcontains': tag_ids
            })
            filtered_host_id = {i.host for i in taghost_instances}
            intersected_host_ids = set(host_ids) and filtered_host_id
            return self.storage.filter(
                Host, **{'id.rcontains': intersected_host_ids}
            )
        else:
            return hosts
