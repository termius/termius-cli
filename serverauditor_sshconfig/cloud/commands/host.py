from operator import attrgetter
from ...core.exceptions import ArgumentRequiredException
from ...core.commands import DetailCommand, ListCommand
from ..models import Host, SshConfig, SshIdentity
from .ssh_config import SshConfigArgs


class HostCommand(DetailCommand):

    """Operate with Host object."""

    allowed_operations = DetailCommand.all_operations

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

        if parsed_args.generate_key:
            raise NotImplementedError('Not implemented')

        if parsed_args.group:
            raise NotImplementedError('Not implemented')

        if parsed_args.ssh_identity:
            raise NotImplementedError('Not implemented')

        identity = SshIdentity()
        identity.username = parsed_args.username
        identity.password = parsed_args.password

        config = SshConfig()
        config.port = parsed_args.port
        config.ssh_identity = identity

        host = Host()
        host.label = parsed_args.label
        host.address = parsed_args.address
        host.ssh_config = config

        with self.storage:
            saved_host = self.storage.save(host)

        self.log_create(saved_host)

    def delete(self, parsed_args):
        if not parsed_args.entry:
            raise ArgumentRequiredException(
                'At least one ID or NAME Address are required.'
            )
        raise NotImplementedError


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
