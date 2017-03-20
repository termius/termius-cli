# -*- coding: utf-8 -*-
"""Acquire SaaS and IaaS hosts."""
import abc
import six

from ...core.commands.mixins import SshConfigMergerMixin
from ...core.models.terminal import Host, SshKey


@six.add_metaclass(abc.ABCMeta)
class BasePortingProvider(SshConfigMergerMixin):
    """Base class for acquiring SaaS and IaaS hosts into storage."""

    def __init__(self, storage, crendetial):
        """Construct new instance for providing hosts from SaaS and IaaS."""
        self.storage = storage
        self.crendetial = crendetial
        self.skipped_hosts = []

    @abc.abstractmethod
    def provider_hosts(self):
        """Override to return host instances from provider."""

    @abc.abstractmethod
    def export_hosts(self):
        """Export hosts to provider format."""

    def import_hosts(self):
        """Import hosts from provider and save it in local storage."""
        hosts_to_import = self.provider_hosts()

        with self.storage:
            for host in hosts_to_import:
                if not self.get_existed_host(host):
                    self.storage.save(host)
                else:
                    self.skipped_hosts.append(host.label)

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
