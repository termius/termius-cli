# -*- coding: utf-8 -*-
"""Module with mixin utils for formatting."""


# pylint: disable=too-few-public-methods
class SshCommandFormatterMixin(object):
    """Mixin formatter for ssh config into ssh command."""

    # pylint: disable=no-self-use
    def render_command(self, ssh_config, address):
        """Generate ssh command call."""
        username = ssh_config.get('ssh_identity', dict()).get('username', '')
        return 'ssh {port} {auth}\n'.format(
            port=format_port(ssh_config['port']),
            auth=ssh_auth(username, address)
        )


def ssh_auth(username, address):
    """Render username and address part."""
    if username:
        return '{}@{}'.format(username, address)
    return '{}'.format(address)


def format_port(port):
    """Render port option."""
    return (port and '-p {}'.format(port)) or ''
