"""Module with init command."""

from argparse import Namespace

import six

from termius.account.commands import LoginCommand
from termius.cloud.commands import PullCommand, PushCommand
from termius.core.commands import AbstractCommand
from termius.sync.commands import SyncCommand


class InitCommand(AbstractCommand):
    """Initialize termius cli."""

    # pylint: disable=no-self-use
    def prompt_username(self):
        """Ask username prompt."""
        return six.moves.input("Termius's username: ")

    # pylint: disable=no-self-use
    def prompt_authy_token(self):
        """Ask authy token prompt."""
        return six.moves.input('Authy token: ')

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument('-u', '--username', metavar='USERNAME')
        parser.add_argument('-p', '--password', metavar='PASSWORD')
        return parser

    def init_namespace(self, parsed_args, username, password):
        """Make authenticated Namespace instance."""
        return Namespace(
            log_file=parsed_args.log_file,
            username=username,
            password=password,
            service='ssh',
            credentials=None
        )

    def login(self, parsed_args):
        """Wrapper for login command."""
        command = LoginCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def pull(self, parsed_args):
        """Wrapper for pull command."""
        command = PullCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def sync_ssh(self, parsed_args):
        """Wrapper for sync command."""
        command = SyncCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def push(self, parsed_args):
        """Wrapper for push command."""
        command = PushCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def take_action(self, parsed_args):
        """Process command call."""
        self.log.info('Initialize Termius CLI...\n')

        username = parsed_args.username or self.prompt_username()
        password = parsed_args.password or self.prompt_password()

        namespace = self.init_namespace(
            parsed_args, username, password
        )

        self.login(namespace)
        self.log.info('\nPull your data from termius cloud...')
        self.pull(namespace)
        self.log.info('\nSync local storage with your ~/.ssh/config...')
        self.sync_ssh(namespace)
        self.log.info('\nPush local data to termius cloud...')
        self.push(namespace)

        self.log.info('\nTermius CLI successfully initialized.')
