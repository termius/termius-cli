# -*- coding: utf-8 -*-
from cliff.formatters.base import SingleFormatter


class SshFormatter(SingleFormatter):

    def add_argument_group(self, parser):
        group = parser.add_argument_group(
            title='formatter to ssh command',
            description='a format a ssh command with arguments',
        )
        group.add_argument(
            '--address',
            action='store',
            help='Use passed address for ssh command',
        )

    def emit_one(self, column_names, data, stdout, parsed_args):
        ssh_config = dict(zip(column_names, data))
        username = ssh_config.get('ssh_identity', dict()).get('username', '')
        address = parsed_args.address or ssh_config['address']
        stdout.write('ssh {port} {auth}\n'.format(
            port=format_port(ssh_config['port']),
            auth=ssh_auth(username, address)
        ))
        return


def ssh_auth(username, address):
    if username:
        return '{}@{}'.format(username, address)
    return '{}'.format(address)


def format_port(port):
    return (port and '-p {}'.format(port)) or ''
