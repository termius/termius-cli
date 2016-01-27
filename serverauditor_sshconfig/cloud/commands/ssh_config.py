# -*- coding: utf-8 -*-
"""Module with Sshconfig's args helper."""
from ..models import SshConfig, SshIdentity


class SshConfigArgs(object):
    """Class for ssh config argument adding and serializing."""

    # pylint: disable=no-self-use
    def add_agrs(self, parser):
        """Add to arg parser ssh config options."""
        parser.add_argument(
            '-p', '--port',
            type=int, metavar='PORT',
            help='Ssh port.'
        )
        parser.add_argument(
            '-S', '--strict-key-check', action='store_true',
            help='Provide to force check ssh server public key.'
        )
        parser.add_argument(
            '-s', '--snippet', metavar='SNIPPET_ID or SNIPPET_NAME',
            help='Snippet id or snippet name.'
        )
        parser.add_argument(
            '--ssh-identity',
            metavar='SSH_IDENTITY', help="Ssh identity's id name or name."
        )
        parser.add_argument(
            '-k', '--keep-alive-packages',
            type=int, metavar='PACKAGES_COUNT',
            help='ServerAliveCountMax option from ssh_config.'
        )
        parser.add_argument(
            '-u', '--username', metavar='SSH_USERNAME',
            help='Username for authenticate to ssh server.'
        )
        parser.add_argument(
            '-P', '--password', metavar='SSH_PASSWORD',
            help='Password for authenticate to ssh server.'
        )
        parser.add_argument(
            '-i', '--identity-file', metavar='IDENTITY_FILE',
            help=('Selects a file from which the identity (private key) '
                  'for public key authentication is read.')
        )
        parser.add_argument(
            'command', nargs='?', metavar='COMMAND',
            help='Create and assign automatically snippet.'
        )
        return parser

    def serialize_args(self, args, instance):
        """Convert args to instance."""
        if instance:
            ssh_identity = (
                instance.ssh_identity
            ) or SshIdentity()
            ssh_config = instance or SshConfig()
        else:
            ssh_config, ssh_identity = SshConfig(), SshIdentity()

        if args.generate_key:
            raise NotImplementedError('Not implemented')

        if args.ssh_identity:
            raise NotImplementedError('Not implemented')

        ssh_identity.username = args.username
        ssh_identity.password = args.password
        ssh_config.port = args.port
        return ssh_config
