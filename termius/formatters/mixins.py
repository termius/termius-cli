# -*- coding: utf-8 -*-
"""Module with mixin utils for formatting."""
from six.moves import shlex_quote


# pylint: disable=too-few-public-methods
class SshCommandFormatterMixin(object):
    """Mixin formatter for ssh config into ssh command."""

    # pylint: disable=no-self-use
    def render_command(self, ssh_config, address, ssh_key_file, pfrule=None):
        """Generate ssh command call."""
        identity = ssh_config.get('identity', dict())
        username = identity.get('username', '')
        return ' '.join([i for i in[
            'ssh',
            format_port(ssh_config['port']),
            format_identity_file(ssh_key_file),
            format_pfrule(pfrule),
            format_strict_host_key(ssh_config['strict_host_key_check']),
            format_use_ssh_key(ssh_config['use_ssh_key']),
            format_timeout(ssh_config['timeout']),
            format_keep_alive_packages(ssh_config['keep_alive_packages']),
            format_agent_forwarding(ssh_config['agent_forwarding']),
            ssh_auth(username, address),
        ] if i]) + '\n'


def ssh_auth(username, address):
    """Render username and address part."""
    if username:
        return '{}@{}'.format(username, address)
    return '{}'.format(address)


def format_identity_file(ssh_key_file):
    """Render identity file option."""
    if ssh_key_file:
        safe_key_path = shlex_quote(str(ssh_key_file))
        return '-i {}'.format(safe_key_path)
    else:
        return ''


def format_port(port):
    """Render port option."""
    return (port and '-p {}'.format(port)) or ''


def format_pfrule(pfrule):
    """Render port forwarding option."""
    format_str = '-{0.pf_type} {binding}'.format
    return (pfrule and format_str(pfrule, binding=pfrule.binding)) or ''


def format_strict_host_key(strict):
    """Render strick host key checking option."""
    format_str = '-o StrictHostKeyChecking={}'.format
    return _bool_to_text(format_str, strict)


def format_use_ssh_key(use_ssh_key):
    """Render identity only option."""
    format_str = '-o IdentitiesOnly={}'.format
    return _bool_to_text(format_str, use_ssh_key)


def format_timeout(timeout):
    """Render server alive interval option."""
    format_str = '-o ServerAliveInterval={}'.format
    return (timeout and format_str(timeout)) or ''


def format_keep_alive_packages(keep_alive_packages):
    """Render server alive count max option."""
    format_str = '-o ServerAliveCountMax={}'.format
    return (keep_alive_packages and format_str(keep_alive_packages)) or ''


def format_agent_forwarding(agent_forwarding):
    """Render server alive count max option."""
    format_str = '-o ForwardAgent={}'.format
    return _bool_to_text(format_str, agent_forwarding)


def _bool_to_text(format_str, value):
    if value is None:
        return ''
    return value and format_str('yes') or format_str('no')
