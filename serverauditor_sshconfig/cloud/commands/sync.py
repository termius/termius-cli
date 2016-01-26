import six
import abc
from base64 import b64decode
from ...core.commands import AbstractCommand
from ..controllers import ApiController
from ..cryptor import RNCryptor
from ...core.storage.strategies import RelatedGetStrategy


@six.add_metaclass(abc.ABCMeta)
class CloudSynchronizationCommand(AbstractCommand):

    def get_parser(self, prog_name):
        parser = super(CloudSynchronizationCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--strategy', metavar='STRATEGY_NAME',
            help='Force to use specific strategy to merge data.'
        )
        parser.add_argument('-p', '--password', metavar='PASSWORD')
        return parser

    @abc.abstractmethod
    def process_sync(self, api_controller):
        pass

    def take_action(self, parsed_args):
        encryption_salt = b64decode(self.config.get('User', 'salt'))
        hmac_salt = b64decode(self.config.get('User', 'hmac_salt'))
        password = parsed_args.get('password', None)
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

    def process_sync(self, api_controller):
        api_controller.post_bulk()
        self.log.info('Push data to Serverauditor cloud.')


class PullCommand(CloudSynchronizationCommand):

    """Pull data from Serverauditor cloud."""

    def process_sync(self, api_controller):
        api_controller.get_bulk()
        self.log.info('Pull data from Serverauditor cloud.')
