# -*- coding: utf-8 -*-
"""Module for pull and push command."""
import abc
from base64 import b64decode
import six
from six.moves import configparser

from ..core.exceptions import AuthyTokenIssue
from ..core.api import API
from ..core.commands import AbstractCommand
from ..core.models.terminal import clean_order
from .client.controllers import ApiController
from .client.cryptor import RNCryptor
from ..core.storage.strategies import RelatedGetStrategy, SyncSaveStrategy


@six.add_metaclass(abc.ABCMeta)
class CloudSynchronizationCommand(AbstractCommand):
    """Base class for pull and push commands."""

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument('-p', '--password', metavar='PASSWORD')
        return parser

    @abc.abstractmethod
    def process_sync(self, api_controller):
        """Do sync staff here."""
        pass

    # pylint: disable=no-self-use
    def prompt_authy_token(self):
        """Ask authy token prompt."""
        return six.moves.input('Authy token: ')

    def take_action(self, parsed_args):
        """Process CLI call."""
        encryption_salt = b64decode(self.config.get('User', 'salt'))
        hmac_salt = b64decode(self.config.get('User', 'hmac_salt'))
        password = parsed_args.password
        if password is None:
            password = self.prompt_password()
        self.validate_password(password)
        cryptor = RNCryptor()
        cryptor.password = password
        cryptor.encryption_salt = encryption_salt
        cryptor.hmac_salt = hmac_salt
        controller = ApiController(self.storage, self.config, cryptor)
        with self.storage:
            self.process_sync(controller)

    def validate_password(self, password):
        """Raise an error when password invalid."""
        username = self.config.get('User', 'username')
        api = API()
        try:
            api.login(username, password)
        except AuthyTokenIssue:
            authy_token = self.prompt_authy_token()
            api.login(username, password, authy_token=authy_token)


class PushCommand(CloudSynchronizationCommand):
    """push data to the Termius Cloud"""

    get_strategy = RelatedGetStrategy
    save_strategy = SyncSaveStrategy

    def process_sync(self, api_controller):
        """Push outdated local instances."""
        try:
            api_controller.put_setting()
            api_controller.post_bulk()
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.log.error('Call pull at first.')
        else:
            self.log.info('Data delivered successfully')


class PullCommand(CloudSynchronizationCommand):
    """pull data from the Termius Cloud"""

    save_strategy = SyncSaveStrategy

    def process_sync(self, api_controller):
        """Pull updated remote instances."""
        api_controller.get_settings()
        api_controller.get_bulk()
        self.log.info('Data successfully collected')


class FullCleanCommand(CloudSynchronizationCommand):
    """remove user data from the Termius Cloud"""

    get_strategy = RelatedGetStrategy
    save_strategy = SyncSaveStrategy

    supported_models = clean_order

    def process_sync(self, api_controller):
        """Pull updated remote instances."""
        api_controller.get_bulk()
        with self.storage:
            self.full_clean()
        api_controller.post_bulk()
        self.log.info('Full clean data from Termius cloud.')

    def full_clean(self):
        """Remove all local and remote instances."""
        for model in self.supported_models:
            self.log.info('Start cleaning %s...', model)
            instances = self.storage.get_all(model)
            for i in instances:
                self.storage.delete(i)
            self.log.info('Complete cleaning')


class CryptoCommand(CloudSynchronizationCommand):
    """encrypt and decrypt text"""

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        super(CryptoCommand, self).extend_parser(parser)
        parser.add_argument(
            '-d', '--decrypt',
            action='store_const', const='decrypt',
            dest='operation'
        )
        parser.add_argument(
            '-e', '--encrypt',
            action='store_const', const='encrypt',
            dest='operation'
        )
        parser.add_argument(
            'text',
            nargs=1,
            metavar='TEXT',
            action='store',
            help='string data'
        )
        return parser

    def process_sync(self, api_controller):
        """Do sync staff here."""
        pass

    def take_action(self, parsed_args):
        """Process decrypt and encrypt text."""
        encryption_salt = b64decode(self.config.get('User', 'salt'))
        hmac_salt = b64decode(self.config.get('User', 'hmac_salt'))
        password = parsed_args.password
        if password is None:
            password = self.prompt_password()
        self.validate_password(password)
        cryptor = RNCryptor()
        cryptor.password = password
        cryptor.encryption_salt = encryption_salt
        cryptor.hmac_salt = hmac_salt

        for i in parsed_args.text:
            result_text = getattr(cryptor, parsed_args.operation)(i)
            self.app.stdout.write('{}\n'.format(result_text))
