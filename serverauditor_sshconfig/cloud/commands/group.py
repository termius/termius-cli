from operator import attrgetter
from ...core.exceptions import (
    InvalidArgumentException, ArgumentRequiredException,
    TooManyEntriesException, DoesNotExistException,
)
from ...core.commands import DetailCommand, ListCommand
from ..models import Group, SshConfig, SshIdentity
from .ssh_config import SshConfigArgs


class GroupCommand(DetailCommand):

    """Operate with Group object."""

    allowed_operations = DetailCommand.all_operations

    def get_parser(self, prog_name):
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

        ssh_config_args = SshConfigArgs()
        ssh_config_args.add_agrs(parser)
        return parser

    def create(self, parsed_args):
        if parsed_args.generate_key:
            raise NotImplementedError('Not implemented')
        if parsed_args.parent_group:
            raise NotImplementedError('Not implemented')
        if parsed_args.ssh_identity:
            raise NotImplementedError('Not implemented')

        identity = SshIdentity()
        identity.username = parsed_args.username
        identity.password = parsed_args.password

        config = SshConfig()
        config.port = parsed_args.port
        config.ssh_identity = identity

        group = Group()
        group.label = parsed_args.label
        group.ssh_config = config

        with self.storage:
            saved_host = self.storage.save(group)
        self.log_create(saved_host)


class GroupsCommand(ListCommand):

    """Manage group objects."""

    def get_parser(self, prog_name):
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

    def take_action(self, parsed_args):
        groups = self.storage.get_all(Group)
        fields = Group.allowed_feilds()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in groups]
