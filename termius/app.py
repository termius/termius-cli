# -*- coding: utf-8 -*-
"""Module for main app class."""
import logging
from os.path import expanduser
from pathlib2 import Path
# pylint: disable=import-error
from cliff.app import App
# pylint: disable=import-error
from cliff.commandmanager import CommandManager

from termius.core.analytics import Analytics
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
            description='Termius app',
            version=__version__,
            command_manager=CommandManager('termius.handlers'),
        )

        self.configure_signals()
        self.directory_path = Path(expanduser('~/.{}/'.format(self.NAME)))
        if not self.directory_path.is_dir():
            self.directory_path.mkdir(parents=True)

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
        self.collect_analytics(cmd)

    def collect_analytics(self, cmd):
        analytics = Analytics(self, getattr(cmd, 'config', None))
        analytics.send_analytics(cmd.cmd_name)
