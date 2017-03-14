# -*- coding: utf-8 -*-
"""Acquire SaaS and IaaS hosts."""
import abc
import six
from pathlib2 import Path
from paramiko.config import SSHConfig

from ...core.commands.mixins import SshConfigMergerMixin
from ...core.models.terminal import Host, SshKey


@six.add_metaclass(abc.ABCMeta)
class BaseSyncService(SshConfigMergerMixin):
    """Base class for acquiring SaaS and IaaS hosts into storage."""

    user_config = '~/.ssh/config'

    def __init__(self, storage, crendetial):
        """Construct new instance for providing hosts from SaaS and IaaS."""
        self.crendetial = crendetial
        self.storage = storage

    @abc.abstractmethod
    def hosts(self):
        """Override to return host instances."""

    def get_ssh_key_label(self, ssh_config):
        if ssh_config['identity'] and ssh_config['identity']['ssh_key']:
            return ssh_config['identity']['ssh_key']['label']

        return None

    def extend_config(self):
        hosts = self.storage.get_all(Host)

        config = SSHConfig()
        with Path(self.user_config).open() as file:
            config.parse(file)

        def make_param(param, value):
            return '\n    %s %s' % (param, value)

        file = open(self.user_config, 'a+')
        file.write('## Termius CLI ##')

        already_existed_hosts = config.get_hostnames()
        for host in hosts:
            if host['address'] in already_existed_hosts or host['label'] in already_existed_hosts:
                continue

            ssh_config = self.get_merged_ssh_config(host)

            host_label = host['label']
            if not len(host_label):
                host_label = host['address']

            host_string = '\nHost %s' % host_label

            host_to_write = {
                'HostName': host['address'],
                'User': host['ssh_config']['identity']['username'],
                'Port': ssh_config['port'] or 22,
            }

            for key, value in host_to_write.iteritems():
                host_string += make_param(key, value)

            host_key_label = self.get_ssh_key_label(ssh_config)

            if host_key_label:
                host_string += make_param(
                    'IdentityFile', '~/.termius/ssh_keys/' + host_key_label
                )

            file.write(host_string + '\n')

    def sync(self):
        """Sync storage content and the Service hosts."""
        self.extend_config()
        service_hosts = self.hosts()
        with self.storage:
            for i in service_hosts:
                updated_i = self.assign_existed_host_ids(i)
                self.storage.save(updated_i)

    def assign_existed_host_ids(self, new_host):
        """Assign to new host existed host id to update it."""
        existed_host = self.get_existed_host(new_host)
        if not existed_host:
            return new_host
        new_host.id = existed_host.id
        new_host.ssh_config.id = existed_host.ssh_config.id
        existed_identity = existed_host.ssh_config.identity
        if not (existed_identity and existed_identity.is_visible):
            new_host.ssh_config.identity.id = existed_identity.id
        if new_host.ssh_config.identity.ssh_key:
            self.assign_ssh_key_ids(new_host.ssh_config.identity.ssh_key)

        return new_host

    def assign_ssh_key_ids(self, new_ssh_key):
        """Assign to new ssh key existed ssh key id to update it."""
        existed_key = self.get_existed_key(new_ssh_key)
        if not existed_key:
            return new_ssh_key
        new_ssh_key.id = existed_key.id
        return new_ssh_key

    def get_existed_host(self, new_host):
        """Retrieve exited host for new host."""
        existed_hosts = self.storage.filter(Host, label=new_host.label)
        return existed_hosts and existed_hosts[0]

    def get_existed_key(self, new_ssh_key):
        """Retrieve exited key for new key."""
        existed_keys = self.storage.filter(SshKey, label=new_ssh_key.label)
        return existed_keys and existed_keys[0]
