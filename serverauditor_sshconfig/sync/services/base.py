# -*- coding: utf-8 -*-
"""Acquire SaaS and IaaS hosts."""
import abc
import six
from ...core.storage import ApplicationStorage


@six.add_metaclass(abc.ABCMeta)
class BaseSyncService(object):
    """Base class for acquiring SaaS and IaaS hosts into storage."""

    def __init__(self, application_name, crendetial):
        """Construct new instance for providing hosts from SaaS and IaaS."""
        self.crendetial = crendetial
        self.storage = ApplicationStorage(application_name)

    @abc.abstractmethod
    def hosts(self):
        """Override to return host instances."""

    def sync(self):
        """Sync storage content and the Service hosts."""
        service_hosts = self.hosts()
        with self.storage:
            for i in service_hosts:
                self.storage.save(i)
