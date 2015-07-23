from base64 import b64decode
from ..core.commands import AbstractCommand
from .controllers import ApiController
from .cryptor import RNCryptor


class PushCommand(AbstractCommand):

    """Push data to Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PushCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--silent', action='store_true',
            help='Do not produce any interactions.'
        )
        parser.add_argument(
            '-S', '--strategy', metavar='STRATEGY_NAME',
            help='Force to use specific strategy to merge data.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Push data to Serverauditor cloud.')


class PullCommand(AbstractCommand):

    """Pull data from Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PullCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--strategy', metavar='STRATEGY_NAME',
            help='Force to use specific strategy to merge data.'
        )
        return parser

    def take_action(self, parsed_args):
        encryption_salt = b64decode(self.config.get('User', 'salt'))
        hmac_salt = b64decode(self.config.get('User', 'hmac_salt'))
        password = self.prompt_password()
        cryptor = RNCryptor()
        cryptor.password = password
        cryptor.encryption_salt = encryption_salt
        cryptor.hmac_salt = hmac_salt
        controller = ApiController(self.storage, self.config, cryptor)
        with self.storage:
            controller.get_bulk()
        self.log.info('Pull data from Serverauditor cloud.')
