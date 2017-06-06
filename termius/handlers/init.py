# -*- coding: utf-8 -*-
"""Module with init command."""

from argparse import Namespace

import six

from termius.account.commands import LoginCommand
from termius.cloud.commands import PullCommand, PushCommand
from termius.core.commands import AbstractCommand
from termius.porting.commands import SSHImportCommand


class InitCommand(AbstractCommand):
    """initialize the Termius CLI"""

    # pylint: disable=no-self-use
    def prompt_username(self):
        """Ask username prompt."""
        self.log.info('Please enter your Termius credentials\n')
        return six.moves.input("Username: ")

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
            password=password
        )

    def login(self, parsed_args):
        """Wrapper for login command."""
        command = LoginCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def pull(self, parsed_args):
        """Wrapper for pull command."""
        command = PullCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def import_ssh(self, parsed_args):
        """Wrapper for sync command."""
        command = SSHImportCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def push(self, parsed_args):
        """Wrapper for push command."""
        command = PushCommand(self.app, self.app_args, self.cmd_name)
        command.take_action(parsed_args)

    def take_action(self, parsed_args):
        """Process command call."""
        self.log.info('Initializing Termius CLI...\n')

        username = parsed_args.username or self.prompt_username()
        password = parsed_args.password or self.prompt_password()

        namespace = self.init_namespace(
            parsed_args, username, password
        )

        self.login(namespace)
        self.log.info('\nCollecting data from the Termius Cloud...')
        self.pull(namespace)
        self.log.info('\nImporting ~/.ssh/config...')
        self.import_ssh(namespace)
        self.log.info('\nPushing data to the Termius Cloud...')
        self.push(namespace)

        self.log.info('\nTermius CLI successfully initialized.')
