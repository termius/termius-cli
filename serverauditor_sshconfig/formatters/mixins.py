# -*- coding: utf-8 -*-
"""Module with mixin utils for formatting."""


# pylint: disable=too-few-public-methods
class SshCommandFormatterMixin(object):
    """Mixin formatter for ssh config into ssh command."""

    # pylint: disable=no-self-use
    def render_command(self, ssh_config, address, ssh_key_file, pfrule=None):
        """Generate ssh command call."""
        ssh_identity = ssh_config.get('ssh_identity', dict())
        username = ssh_identity.get('username', '')
        return ' '.join([i for i in[
            'ssh',
            format_port(ssh_config['port']),
            format_ssh_identity_file(ssh_key_file),
            format_pfrule(pfrule),
            ssh_auth(username, address),
        ] if i]) + '\n'


def ssh_auth(username, address):
    """Render username and address part."""
    if username:
        return '{}@{}'.format(username, address)
    return '{}'.format(address)


def format_ssh_identity_file(ssh_key_file):
    """Render identity file option."""
    return (ssh_key_file and '-i {}'.format(ssh_key_file)) or ''


def format_port(port):
    """Render port option."""
    return (port and '-p {}'.format(port)) or ''


def format_pfrule(pfrule):
    """Render port forwarding option."""
    format_str = '-{0.pf_type} {binding}'.format
    return (pfrule and format_str(pfrule, binding=pfrule.binding)) or ''
