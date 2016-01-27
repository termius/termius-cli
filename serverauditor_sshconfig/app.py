# -*- coding: utf-8 -*-
"""Module for main app class."""
import logging
# pylint: disable=import-error
from cliff.app import App
# pylint: disable=import-error
from cliff.commandmanager import CommandManager

from . import get_version


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

    def configure_logging(self):
        """Change logging level for request package."""
        super(ServerauditorApp, self).configure_logging()
        logging.getLogger('requests').setLevel(logging.WARNING)
        return
