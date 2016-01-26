
class SshConfigArgs(object):

    def add_agrs(self, parser):
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
