from operator import attrgetter
from ...core.exceptions import ArgumentRequiredException
from ...core.commands import DetailCommand, ListCommand
from ..models import Host, SshConfig, SshIdentity
from .ssh_config import SshConfigArgs


class HostCommand(DetailCommand):
    """Operate with Host object."""

    allowed_operations = DetailCommand.all_operations
    model_class = Host

    def get_parser(self, prog_name):
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

        ssh_config_args = SshConfigArgs()
        ssh_config_args.add_agrs(parser)
        return parser

    def create(self, parsed_args):
        if not parsed_args.address:
            raise ArgumentRequiredException('Address is required.')

        self.create_instance(parsed_args)

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        if instance:
            ssh_identity = (
                instance.ssh_config and instance.ssh_config.ssh_identity
            ) or SshIdentity()
            ssh_config = instance.ssh_config or SshConfig()
            host = instance
        else:
            host, ssh_config, ssh_identity = Host(), SshConfig(), SshIdentity()

        if args.generate_key:
            raise NotImplementedError('Not implemented')

        if args.group:
            raise NotImplementedError('Not implemented')

        if args.ssh_identity:
            raise NotImplementedError('Not implemented')

        ssh_identity.username = args.username
        ssh_identity.password = args.password
        ssh_config.port = args.port
        host.label = args.label
        host.address = args.address

        ssh_config.ssh_identity = ssh_identity
        host.ssh_config = ssh_config
        return host


class HostsCommand(ListCommand):
    """Manage host objects."""

    def get_parser(self, prog_name):
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

    def take_action(self, parsed_args):
        hosts = self.storage.get_all(Host)
        fields = Host.allowed_fields()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in hosts]
