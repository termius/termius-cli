import abc
import six
from ...core.storage import ApplicationStorage


@six.add_metaclass(abc.ABCMeta)
class BaseSyncService(object):

    def __init__(self, application_name, crendetial):
        self.crendetial = crendetial
        self.storage = ApplicationStorage(application_name)

    @abc.abstractmethod
    def hosts(self):
        """Override to return host instances."""

    def sync(self):
        service_hosts = self.hosts()
        with self.storage:
            for i in service_hosts:
                self.storage.save(i)
