# -*- coding: utf-8 -*-
"""Module for pull and push command."""
import abc
from base64 import b64decode
import six
from ...core.commands import AbstractCommand
from ..client.controllers import ApiController
from ..client.cryptor import RNCryptor
from ...core.storage.strategies import RelatedGetStrategy, SyncSaveStrategy


@six.add_metaclass(abc.ABCMeta)
class CloudSynchronizationCommand(AbstractCommand):
    """Base class for pull and push commands."""

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(CloudSynchronizationCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--strategy', metavar='STRATEGY_NAME',
            help='Force to use specific strategy to merge data.'
        )
        parser.add_argument('-p', '--password', metavar='PASSWORD')
        return parser

    @abc.abstractmethod
    def process_sync(self, api_controller):
        """Do sync staff here."""
        pass

    def take_action(self, parsed_args):
        """Process CLI call."""
        encryption_salt = b64decode(self.config.get('User', 'salt'))
        hmac_salt = b64decode(self.config.get('User', 'hmac_salt'))
        password = parsed_args.password
        if password is None:
            password = self.prompt_password()
        cryptor = RNCryptor()
        cryptor.password = password
        cryptor.encryption_salt = encryption_salt
        cryptor.hmac_salt = hmac_salt
        controller = ApiController(self.storage, self.config, cryptor)
        with self.storage:
            self.process_sync(controller)


class PushCommand(CloudSynchronizationCommand):
    """Push data to Serverauditor cloud."""

    get_strategy = RelatedGetStrategy
    save_strategy = SyncSaveStrategy

    def process_sync(self, api_controller):
        """Push outdated local instances."""
        api_controller.post_bulk()
        self.log.info('Push data to Serverauditor cloud.')


class PullCommand(CloudSynchronizationCommand):
    """Pull data from Serverauditor cloud."""

    save_strategy = SyncSaveStrategy

    def process_sync(self, api_controller):
        """Pull updated remote instances."""
        api_controller.get_bulk()
        self.log.info('Pull data from Serverauditor cloud.')
