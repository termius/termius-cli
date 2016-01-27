from operator import attrgetter
from ...core.commands import DetailCommand, ListCommand
from ..models import Group, SshConfig, SshIdentity
from .ssh_config import SshConfigArgs


class GroupCommand(DetailCommand):
    """Operate with Group object."""

    allowed_operations = DetailCommand.all_operations
    model_class = Group

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
        self.create_instance(parsed_args)

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        if instance:
            ssh_identity = (
                instance.ssh_config and instance.ssh_config.ssh_identity
            ) or SshIdentity()
            ssh_config = instance.ssh_config or SshConfig()
            group = instance
        else:
            group, ssh_config, ssh_identity = (
                Group(), SshConfig(), SshIdentity()
            )

        if args.generate_key:
            raise NotImplementedError('Not implemented')
        if args.parent_group:
            raise NotImplementedError('Not implemented')
        if args.ssh_identity:
            raise NotImplementedError('Not implemented')

        ssh_identity.username = args.username
        ssh_identity.password = args.password

        ssh_config.port = args.port
        ssh_config.ssh_identity = ssh_identity

        group.label = args.label
        group.ssh_config = ssh_config
        return group


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
        fields = Group.allowed_fields()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in groups]
