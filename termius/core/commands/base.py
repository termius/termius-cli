# -*- coding: utf-8 -*-
"""Module with comprehensive base commands."""
import logging

# pylint: disable=import-error
from cliff.command import Command
from google_measurement_protocol import Event, report

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
        parser.add_argument('--log-file', help='Path to log file.')
        return self.extend_parser(parser)

    # pylint: disable=no-self-use
    def extend_parser(self, parser):
        """Add more arguments to parser."""
        return parser

    def run(self, parsed_args):
        """Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        Developers creating new command base classes (such as
        :class:`Lister` and :class:`ShowOne`) should override this
        method to wrap :meth:`take_action`.

        Return the value returned by :meth:`take_action` or 0.
        """
        self.send_analytics()
        return super(AbstractCommand, self).run(parsed_args)

    def send_analytics(self):
        event = self.generate_event()
        client_id = self.config
        report(self.tracking_id, client_id, event)

    def generate_event(self):
        return Event('profile', 'settings')

    @property
    def tracking_id(self):
        return 'UA-92775225-1'
