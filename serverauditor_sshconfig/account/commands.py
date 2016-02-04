# -*- coding: utf-8 -*-
"""Module to keep login and logout command."""
import six
from ..core.commands import AbstractCommand
from .managers import AccountManager


# pylint: disable=abstract-method
class BaseAccountCommand(AbstractCommand):
    """Base class for login and logout commands."""

    def __init__(self, app, app_args, cmd_name=None):
        """Construct new instance."""
        super(BaseAccountCommand, self).__init__(app, app_args, cmd_name)
        self.manager = AccountManager(self.config)


class LoginCommand(BaseAccountCommand):
    """Sign into serverauditor cloud."""

    # pylint: disable=no-self-use
    def prompt_username(self):
        """Ask username prompt."""
        return six.moves.input("Serverauditor's username: ")

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument('-u', '--username', metavar='USERNAME')
        parser.add_argument('-p', '--password', metavar='PASSWORD')
        return parser

    def take_action(self, parsed_args):
        """Process CLI call."""
        username = parsed_args.username or self.prompt_username()
        password = parsed_args.password or self.prompt_password()
        self.manager.login(username, password)
        self.log.info('Sign into serverauditor cloud.')


class LogoutCommand(BaseAccountCommand):
    """Sign out serverauditor cloud."""

    def take_action(self, _):
        """Process CLI call."""
        self.manager.logout()
        self.log.info('Sign out serverauditor cloud.')
