from operator import attrgetter
from ...core.commands import DetailCommand, ListCommand
from ..models import SshIdentity


class SshIdentityCommand(DetailCommand):

    """Operate with ssh identity object."""

    allowed_operations = DetailCommand.all_operations
    model_class = SshIdentity

    def get_parser(self, prog_name):
        parser = super(SshIdentityCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--generate-key', action='store_true',
            help='Create and assign automatically a identity file for host.'
        )
        parser.add_argument(
            '-u', '--username',
            metavar='USERNAME', help="Username of host's user."
        )
        parser.add_argument(
            '-p', '--password',
            metavar='PASSWORD', help="Password of Host's user."
        )
        parser.add_argument(
            '-i', '--identity-file',
            metavar='PRIVATE_KEY', help="Private key."
        )
        parser.add_argument(
            '-k', '--ssh-key',
            metavar='SSH_KEY', help="Serveraduitor's ssh key's name or id."
        )
        parser.add_argument(
            'ssh_identity', nargs='*', metavar='IDENITY_ID or IDENITY_NAME',
            help='Pass to edit exited identities.'
        )
        return parser

    def create(self, parsed_args):
        self.create_instance(parsed_args)

    def serialize_args(self, args, instance=None):
        if instance:
            identity = instance
        else:
            identity = SshIdentity()

        if args.generate_key:
            raise NotImplementedError('Not implemented')

        if args.identity_file:
            raise NotImplementedError('Not implemented')

        if args.ssh_key:
            raise NotImplementedError('Not implemented')

        identity.username = args.username
        identity.password = args.password
        return identity


class SshIdentitiesCommand(ListCommand):

    """Manage ssh identity objects."""

    def take_action(self, parsed_args):
        ssh_identities = self.storage.get_all(SshIdentity)
        fields = SshIdentity.allowed_fields()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in ssh_identities]
