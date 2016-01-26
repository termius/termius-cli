# coding: utf-8
import logging
# pylint: disable=import-error
from cliff.app import App
# pylint: disable=import-error
from cliff.commandmanager import CommandManager

from . import get_version


class ServerauditorApp(object, App):

    def __init__(self):
        super(ServerauditorApp, self).__init__(
            description='Serverauditor app',
            version=get_version(),
            command_manager=CommandManager('serverauditor.handlers'),
        )

    def configure_logging(self):
        super(ServerauditorApp, self).configure_logging()
        logging.getLogger('requests').setLevel(logging.WARNING)
        return
