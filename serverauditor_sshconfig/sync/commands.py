# coding: utf-8
from ..core.commands import AbstractCommand
from .servicemanager import ServicesManager


class NoSuchServiceException(Exception):
    pass


class SyncCommand(AbstractCommand):

    """Sync with IaaS or PaaS."""

    service_manager = ServicesManager('serverauditor.sync.services')

    def get_parser(self, prog_name):
        parser = super(SyncCommand, self).get_parser(prog_name)
        parser.add_argument('-c', '--credentials')
        parser.add_argument('service', metavar='SERVICE')
        return parser

    def get_service(self, service_name):
        try:
            service_class, _ = self.service_manager.find_service(
                service_name
            )
        except KeyError:
            raise NoSuchServiceException(
                'Do not support service: {}.'.format(service_name)
            )
        return service_class

    def sync_with_service(self, service, credentials):
        service_class = self.get_service(service)
        service = service_class(credentials)
        service.sync()

    def take_action(self, parsed_args):
        self.sync_with_service(parsed_args.service,
                               parsed_args.credentials)
        self.log.info('Sync with service %s.', parsed_args.service)
