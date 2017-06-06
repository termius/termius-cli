# -*- coding: utf-8 -*-
"""Module for main app class."""
import logging
import os

from os.path import expanduser
from pathlib2 import Path
# pylint: disable=import-error
from cliff.app import App
# pylint: disable=import-error
from cliff.commandmanager import CommandManager
from cliff import argparse

from termius.core.analytics import Analytics
from termius.core.commands.help import HelpCommand, HelpAction
from . import __version__
from .core.signals import (
    post_create_instance,
    post_update_instance,
    post_delete_instance,
    post_logout,
)
from .core.subscribers import (
    store_ssh_key, delete_ssh_key,
    clean_data
)
from .core.models.terminal import SshKey


# pylint: disable=too-few-public-methods
class TermiusApp(App):
    """Class for CLI application."""

    def __init__(self):
        """Construct new CLI application."""
        super(TermiusApp, self).__init__(
            description='Termius - crossplatform SSH and Telnet client',
            version=__version__,
            command_manager=CommandManager('termius.handlers'),
        )

        self.configure_signals()
        self.directory_path = Path(expanduser('~/.{}/'.format(self.NAME)))
        if not self.directory_path.is_dir():
            self.directory_path.mkdir(parents=True)

        self.command_manager.add_command('help', HelpCommand)

    def configure_logging(self):
        """Change logging level for request package."""
        super(TermiusApp, self).configure_logging()
        logging.getLogger('requests').setLevel(logging.WARNING)
        return

    # pylint: disable=no-self-use
    def configure_signals(self):
        """Bind subscribers to signals."""
        post_create_instance.connect(store_ssh_key, sender=SshKey)
        post_update_instance.connect(store_ssh_key, sender=SshKey)
        post_delete_instance.connect(delete_ssh_key, sender=SshKey)

        post_logout.connect(clean_data)

    def prepare_to_run_command(self, cmd):
        """Collect analytics if it`s not disabled."""
        if os.getenv('NOT_COLLECT_STAT'):
            return

        self.collect_analytics(cmd)

    def collect_analytics(self, cmd):
        """Make Analytics instance and send analytics."""
        analytics = Analytics(self, getattr(cmd, 'config', None))
        analytics.send_analytics(cmd.cmd_name)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
            help='display version information and exit'
        )
        verbose_group = parser.add_mutually_exclusive_group()
        verbose_group.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='provide a detailed output',
        )
        verbose_group.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='display warnings and errors only',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='record output into a designated file',
        )
        if self.deferred_help:
            parser.add_argument(
                '-h', '--help',
                dest='deferred_help',
                action='store_true',
                help="display help message",
            )
        else:
            parser.add_argument(
                '-h', '--help',
                action=HelpAction,
                nargs=0,
                default=self,  # tricky
                help="show the help message",
            )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='enable debugging mode',
        )
        return parser
