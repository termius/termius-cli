# -*- coding: utf-8 -*-
"""Module to keep login and logout command."""
from contextlib import contextmanager
import six
from ..core.commands import AbstractCommand
from ..core.signals import post_logout
from ..core.commands.arg_types import boolean_yes_no
from ..core.exceptions import OptionNotSetException
from .managers import AccountManager


@contextmanager
def on_clean_when_logout(command, manager):
    """Monitor is account changed and call data clean."""
    try:
        old_username = manager.username
    except OptionNotSetException:
        old_username = None
    yield
    try:
        new_username = manager.username
    except OptionNotSetException:
        new_username = None

    is_username_changed = (
        old_username and old_username != new_username
    )
    if is_username_changed:
        post_logout.send(command, command=command, email=old_username)


# pylint: disable=abstract-method
class BaseAccountCommand(AbstractCommand):
    """Base class for login and logout commands."""

    def __init__(self, app, app_args, cmd_name=None):
        """Construct new instance."""
        super(BaseAccountCommand, self).__init__(app, app_args, cmd_name)
        self.manager = AccountManager(self.config)


class LoginCommand(BaseAccountCommand):
    """Sign into Termius cloud."""

    # pylint: disable=no-self-use
    def prompt_username(self):
        """Ask username prompt."""
        return six.moves.input("Termius's username: ")

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument('-u', '--username', metavar='USERNAME')
        parser.add_argument('-p', '--password', metavar='PASSWORD')
        return parser

    def take_action(self, parsed_args):
        """Process CLI call."""
        username = parsed_args.username or self.prompt_username()
        password = parsed_args.password or self.prompt_password()
        with on_clean_when_logout(self, self.manager):
            self.manager.login(username, password)
        self.log.info('Sign into Termius cloud.')


class LogoutCommand(BaseAccountCommand):
    """Sign out Termius cloud."""

    def take_action(self, _):
        """Process CLI call."""
        with on_clean_when_logout(self, self.manager):
            self.manager.logout()
        self.log.info('Sign out Termius cloud.')


class SettingsCommand(BaseAccountCommand):
    """Update account settings."""

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '--synchronize-key', action='store', type=boolean_yes_no,
            choices=(False, True), default=True,
            help='Sync ssh keys and ssh identities or not.'
        )
        parser.add_argument(
            '--agent-forwarding', action='store', type=boolean_yes_no,
            choices=(False, True), default=True,
            help='Sync ssh keys and ssh identities or not.'
        )
        return parser

    def take_action(self, args):
        """Process CLI call."""
        settings = {
            k: getattr(args, k)
            for k in ('synchronize_key', 'agent_forwarding')
        }
        self.manager.set_settings(settings)
        self.log.info('Set settings.')
