# -*- coding: utf-8 -*-
"""Module with adapter for ssh config hosts."""
from os import environ

from pathlib2 import Path

from termius.core.commands.mixins import SshConfigMergerMixin
from termius.core.models.terminal import Host, SshConfig, Identity, SshKey


class SSHConfigHostAdapter(SshConfigMergerMixin):
    """Class for adapting app host and ssh config hosts."""

    default_user = environ.get('USER', None)

    def get_instance_ssh_key_label(self, ssh_config):
        """Helper to retrieve ssh_key lable."""
        if ssh_config['identity'] and ssh_config['identity']['ssh_key']:
            return ssh_config['identity']['ssh_key']['label']

        return None

    def create_key(self, config):
        """Construct new application ssh key instance."""
        if 'identityfile' not in config:
            return None
        identityfile = self.choose_ssh_key(config['identityfile'], config)
        if not identityfile:
            return None
        content = identityfile.read_text()
        return SshKey(label=identityfile.name, private_key=content)

    # pylint: disable=unused-argument,no-self-use
    def choose_ssh_key(self, sshkeys, host_config):
        """Choose single ssh key path instance from ones."""
        key_paths = [Path(i) for i in sshkeys]
        existed_paths = [i for i in key_paths if i.is_file()]
        return existed_paths and existed_paths[0]

    def adapt_instance_to_ssh_config_host(self, host_instance):
        """Convert app host to ssh config host."""
        ssh_config = self.get_merged_ssh_config(host_instance)

        adapted = {
            'hostname': host_instance['address'],
            'user': ssh_config['identity']['username'],
            'port': ssh_config['port'] or 22
        }

        host_key_label = self.get_instance_ssh_key_label(ssh_config)

        if host_key_label:
            adapted.update(
                identityfile='~/.termius/ssh_keys/' + host_key_label
            )

        return adapted

    def adapt_ssh_config_host_to_instance(self, alias, parsed_host):
        """Convert parsed host to application host."""
        app_host = Host(
            label=alias,
            address=parsed_host['hostname'],
        )
        ssh_config = SshConfig(
            identity=Identity(
                username=parsed_host.get('user', self.default_user),
                ssh_key=self.create_key(parsed_host),
                is_visible=False,
                label=app_host.label
            )
        )

        ssh_config.port = parsed_host.get('port')
        ssh_config.timeout = parsed_host.get('serveraliveinterval')
        ssh_config.keep_alive_packages = parsed_host.get('serveralivecountmax')
        ssh_config.use_ssh_key = parsed_host.get('identitiesonly')
        ssh_config.strict_host_key_check = parsed_host.get(
            'stricthostkeychecking'
        )

        app_host.ssh_config = ssh_config

        return app_host
