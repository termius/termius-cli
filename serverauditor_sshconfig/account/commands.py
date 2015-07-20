# coding: utf-8
"""
Copyright (c) 2013 Crystalnix.
License BSD, see LICENSE for more details.
"""
import six
from getpass import getpass
from ..core.commands import AbstractCommand
from .managers import AccountManager


class LoginCommand(AbstractCommand):

    """Sign into serverauditor cloud."""

    def prompt_username(self):
        return six.moves.input("Serverauditor's username: ")

    def prompt_password(self):
        return getpass("Serverauditor's password: ")

    def get_parser(self, prog_name):
        parser = super(LoginCommand, self).get_parser(prog_name)
        parser.add_argument('-u', '--username', metavar='USERNAME')
        parser.add_argument('--sync-sshconfig', action='store_true')
        return parser

    def take_action(self, parsed_args):
        manager = AccountManager(self.app.NAME)
        username = parsed_args.username or self.prompt_username()
        password = self.prompt_password()
        manager.login(username, password)
        self.log.info('Sign into serverauditor cloud.')


class LogoutCommand(AbstractCommand):

    """Sign out serverauditor cloud."""

    def get_parser(self, prog_name):
        parser = super(LogoutCommand, self).get_parser(prog_name)
        parser.add_argument('--clear-sshconfig', action='store_true')
        return parser

    def take_action(self, parsed_args):
        manager = AccountManager(self.app.NAME)
        manager.logout()
        self.log.info('Sign out serverauditor cloud.')
