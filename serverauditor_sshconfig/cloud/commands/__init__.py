from base64 import b64decode
from ...core.commands import AbstractCommand
from ..controllers import ApiController
from ..cryptor import RNCryptor

from .host import HostCommand, HostsCommand
from .group import GroupCommand, GroupsCommand
from .snippet import SnippetCommand, SnippetsCommand
from .pf_rule import PFRuleCommand, PFRulesCommand
from .ssh_identity import SshIdentityCommand, SshIdentitiesCommand
from .tag import TagsCommand


class PushCommand(AbstractCommand):

    """Push data to Serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(PushCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--strategy', metavar='STRATEGY_NAME',
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


class UseGroupCommand(AbstractCommand):

    """Change group."""

    def get_parser(self, prog_name):
        parser = super(UseGroupCommand, self).get_parser(prog_name)
        parser.add_argument(
            'group', metavar='GROUP_ID or GROUP_NAME',
            help='This group name will be used as default group.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info('Use Group.')


class InfoCommand(AbstractCommand):

    """Show info about host or group."""

    def get_parser(self, prog_name):
        parser = super(InfoCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-G', '--group', dest='entry_type',
            action='store_const', const='group',
            help='Show info about group.'
        )
        parser.add_argument(
            '-H', '--host', dest='entry_type',
            action='store_const', const='host',
            help='Show info about host.'
        )
        parser.add_argument(
            '-M', '--no-merge', action='store_true',
            help='Do not merge configs.'
        )
        parser.add_argument(
            '--ssh', action='store_true',
            help='Show info in ssh_config format'
        )
        parser.add_argument('id_or_name', metavar='ID or NAME')
        return parser

    def take_action(self, parsed_args):
        self.log.info('Info about group or host.')
