# -*- coding: utf-8 -*-
"""Module for ssh identity command."""
from ..core.commands import DetailCommand, ListCommand
from ..core.models.terminal import SshIdentity, SshKey
from ..core.exceptions import InvalidArgumentException
from .ssh_key import SshKeyGeneratorMixin


class SshIdentityCommand(SshKeyGeneratorMixin, DetailCommand):
    """Operate with ssh identity object."""

    model_class = SshIdentity

    def extend_parser(self, parser):
        """Add more arguments to parser."""
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
            metavar='PRIVATE_KEY', help='Private key.'
        )
        parser.add_argument(
            '-k', '--ssh-key',
            metavar='SSH_KEY', help="Serveraduitor's ssh key's name or id."
        )
        return parser

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        if instance:
            identity = instance
        else:
            identity = SshIdentity()
        ssh_key = None

        self.check_incompatible_args(args)

        if args.identity_file:
            ssh_key = self.generate_ssh_key_instance(args)

        if args.ssh_key:
            ssh_key = self.get_relation(SshKey, args.ssh_key)

        identity.username = args.username
        identity.password = args.password
        identity.is_visible = True
        if ssh_key:
            identity.ssh_key = ssh_key
        return identity

    def check_incompatible_args(self, args):
        """Raise an error when passed incompatible args."""
        if args.identity_file and args.ssh_key:
            raise InvalidArgumentException(
                'You can not use ssh key and identity file together!'
            )


class SshIdentitiesCommand(ListCommand):
    """Manage ssh identity objects."""

    model_class = SshIdentity
