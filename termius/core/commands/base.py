# -*- coding: utf-8 -*-
"""Module with comprehensive base commands."""
import logging

from cliff.command import Command

from ..settings import Config
from ..storage import ApplicationStorage
from ..storage.strategies import (
    SaveStrategy,
    GetStrategy,
    SoftDeleteStrategy,
)
from .mixins import PasswordPromptMixin


# pylint: disable=abstract-method
class AbstractCommand(PasswordPromptMixin, Command):
    """Abstract Command with log."""

    log = logging.getLogger(__name__)

    save_strategy = SaveStrategy
    get_strategy = GetStrategy
    delete_strategy = SoftDeleteStrategy

    skip_fields = ['remote_instance']

    def __init__(self, app, app_args, cmd_name=None):
        """Construct new command."""
        super(AbstractCommand, self).__init__(app, app_args, cmd_name)
        self.config = Config(self)
        self.storage = ApplicationStorage(
            self,
            save_strategy=self.save_strategy,
            get_strategy=self.get_strategy,
            delete_strategy=self.delete_strategy
        )

    def get_parser(self, prog_name):
        """Create command line argument parser."""
        parser = super(AbstractCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--log-file', help='record output to FILE'
        )
        return self.extend_parser(parser)

    # pylint: disable=no-self-use
    def extend_parser(self, parser):
        """Add more arguments to parser."""
        return parser
