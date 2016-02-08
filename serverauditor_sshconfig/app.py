# -*- coding: utf-8 -*-
"""Module for main app class."""
import logging
from os.path import expanduser
from pathlib import Path
# pylint: disable=import-error
from cliff.app import App
# pylint: disable=import-error
from cliff.commandmanager import CommandManager

from . import get_version
from .core.signals import (
    post_create_instance,
    post_update_instance,
    post_delete_instance,
)
from .core.subscribers import store_ssh_key, delete_ssh_key
from .core.models.terminal import SshKey


# pylint: disable=too-few-public-methods
class ServerauditorApp(App):
    """Class for CLI application."""

    def __init__(self):
        """Construct new CLI application."""
        super(ServerauditorApp, self).__init__(
            description='Serverauditor app',
            version=get_version(),
            command_manager=CommandManager('serverauditor.handlers'),
        )
        self.configure_signals()
        self.directory_path = Path(expanduser('~/.{}/'.format(self.NAME)))
        if not self.directory_path.is_dir():
            self.directory_path.mkdir(parents=True)

    def configure_logging(self):
        """Change logging level for request package."""
        super(ServerauditorApp, self).configure_logging()
        logging.getLogger('requests').setLevel(logging.WARNING)
        return

    def configure_signals(self):
        post_create_instance.connect(store_ssh_key, sender=SshKey)
        post_update_instance.connect(store_ssh_key, sender=SshKey)
        post_delete_instance.connect(delete_ssh_key, sender=SshKey)
