# coding: utf-8
import inspect
import pkg_resources


class ServicesManager(object):

    def __init__(self, namespace):
        self.commands = {}
        self.namespace = namespace
        self.load_services(self.namespace)

    def load_services(self, namespace):
        for ep in pkg_resources.iter_entry_points(namespace):
            service_name = ep.name
            self.commands[service_name] = ep

    def find_service(self, service):
        service_ep = self.commands[service]
        if hasattr(service_ep, 'resolve'):
            service_factory = service_ep.resolve()
        else:
            # NOTE(dhellmann): Some fake classes don't take
            # require as an argument. Yay?
            arg_spec = inspect.getargspec(service_ep.load)
            if 'require' in arg_spec[0]:
                service_factory = service_ep.load(require=False)
            else:
                service_factory = service_ep.load()
        return (service_factory, service)
