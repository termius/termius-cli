# -*- coding: utf-8 -*-
"""Acquire SaaS and IaaS hosts."""
import abc
import six
from ...core.models.terminal import Host, SshKey


@six.add_metaclass(abc.ABCMeta)
class BaseSyncService(object):
    """Base class for acquiring SaaS and IaaS hosts into storage."""

    def __init__(self, storage, crendetial):
        """Construct new instance for providing hosts from SaaS and IaaS."""
        self.crendetial = crendetial
        self.storage = storage

    @abc.abstractmethod
    def hosts(self):
        """Override to return host instances."""

    def sync(self):
        """Sync storage content and the Service hosts."""
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
        existed_ssh_identity = existed_host.ssh_config.ssh_identity
        if not (existed_ssh_identity and existed_ssh_identity.is_visible):
            new_host.ssh_config.ssh_identity.id = existed_ssh_identity.id
        if new_host.ssh_config.ssh_identity.ssh_key:
            self.assign_ssh_key_ids(new_host.ssh_config.ssh_identity.ssh_key)

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
