# coding: utf-8
from .core.commands import AbstractCommand


class ConnectCommand(AbstractCommand):
    """Connect to specific host."""

    def get_parser(self, prog_name):
        parser = super(ConnectCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-G', '--group', metavar='GROUP_ID or GROUP_NAME',
            help=("Use this group's (default is active group) config "
                  "to merge with host's config.")
        )
        parser.add_argument(
            '--ssh', metavar='SSH_CONFIG_OPTIONS',
            help='Options in ssh_config format.'
        )
        parser.add_argument(
            'host', metavar='HOST_ID or HOST_NAME',
            help='Connect to this host.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Connect to host %s.', parsed_args['host'])
