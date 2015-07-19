# coding: utf-8

from cliff.app import App
from cliff.commandmanager import CommandManager

from . import __version__


def get_version():
    return '.'.join(map(str, __version__))


class ServerauditorApp(App):

    def __init__(self):
        super(ServerauditorApp, self).__init__(
            description='Serverauditor app',
            version=get_version(),
            command_manager=CommandManager('serverauditor.handlers'),
        )
