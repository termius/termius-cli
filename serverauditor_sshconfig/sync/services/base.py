import six
import abc


@six.add_metaclass(abc.ABCMeta)
class BaseSyncService(object):

    def __init__(self, crendetial):
        self.crendetial = crendetial

    @abc.abstractmethod
    def hosts(self):
        """Override to return host instances."""

    def sync(self):
        service_hosts = self.hosts()
