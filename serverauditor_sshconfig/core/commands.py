# -*- coding: utf-8 -*-
"""Module with base CLI commands."""
import logging
import getpass

# pylint: disable=import-error
from cliff.command import Command
# pylint: disable=import-error
from cliff.lister import Lister
from .exceptions import DoesNotExistException, ArgumentRequiredException
from .settings import Config
from .storage import ApplicationStorage
from .storage.strategies import (
    SaveStrategy,
    GetStrategy,
    DeleteStrategy,
    RelatedSaveStrategy,
    RelatedGetStrategy,
    SoftDeleteStrategy,
)


# pylint: disable=too-few-public-methods
class PasswordPromptMixin(object):
    """Mixin to command to call account password prompt."""

    # pylint: disable=no-self-use
    def prompt_password(self):
        """Ask user to enter password in secure way."""
        return getpass.getpass("Serverauditor's password:")


# pylint: disable=abstract-method
class AbstractCommand(PasswordPromptMixin, Command):
    """Abstract Command with log."""

    log = logging.getLogger(__name__)

    save_strategy = SaveStrategy
    get_strategy = GetStrategy
    delete_strategy = DeleteStrategy

    def __init__(self, app, app_args, cmd_name=None):
        """Construct new command."""
        super(AbstractCommand, self).__init__(app, app_args, cmd_name)
        self.config = Config(self.app.NAME)
        self.storage = ApplicationStorage(
            self.app.NAME,
            save_strategy=self.save_strategy,
            get_strategy=self.get_strategy,
            delete_strategy=self.delete_strategy
        )

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(AbstractCommand, self).get_parser(prog_name)
        parser.add_argument('--log-file', help='Path to log file.')
        return parser


class DetailCommand(AbstractCommand):
    """Command for operating with models by id or names."""

    save_strategy = RelatedSaveStrategy
    get_strategy = RelatedGetStrategy
    delete_strategy = SoftDeleteStrategy

    all_operations = {'delete', 'update', 'create'}
    allowed_operations = set()
    """Allowed operations for detail command.

    E.g. allowed_operations = {'delete', 'update', 'create'}
    """

    def __init__(self, *args, **kwargs):
        """Construct new detail command."""
        super(DetailCommand, self).__init__(*args, **kwargs)
        assert self.all_operations.intersection(self.allowed_operations)

    def update(self, parsed_args):
        """Handle update command.

        Get models from storage, parse args and update models.
        """
        if not parsed_args.entry:
            raise ArgumentRequiredException(
                'At least one ID or NAME are required.'
            )
        instances = self.get_objects(parsed_args.entry)
        for i in instances:
            self.update_instance(parsed_args, i)

    def delete(self, parsed_args):
        """Handle delete command.

        Get models from storage, delete models.
        """
        if not parsed_args.entry:
            raise ArgumentRequiredException(
                'At least one ID or NAME are required.'
            )
        instances = self.get_objects(parsed_args.entry)
        for i in instances:
            self.delete_instance(i)

    @property
    def is_allow_delete(self):
        """Check is command handle model deleting."""
        return 'delete' in self.allowed_operations

    @property
    def is_allow_update(self):
        """Check is command handle model updating."""
        return 'update' in self.allowed_operations

    @property
    def is_allow_create(self):
        """Check is command handle model creating."""
        return 'create' in self.allowed_operations

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(DetailCommand, self).get_parser(prog_name)
        if self.is_allow_delete:
            parser.add_argument(
                '-d', '--delete',
                action='store_true', help='Delete entries.'
            )
        if self.is_allow_create or self.is_allow_update:
            parser.add_argument(
                '-I', '--interactive', action='store_true',
                help='Enter to interactive mode.'
            )
            parser.add_argument(
                '-L', '--label', metavar='NAME',
                help="Entry's label in Serverauditor"
            )
        if self.is_allow_delete or self.is_allow_update:
            parser.add_argument(
                'entry', nargs='*', metavar='ID or NAME',
                help='Pass to edit exited entries.'
            )

        return parser

    def take_action(self, parsed_args):
        """Process CLI call."""
        if self.is_allow_delete and parsed_args.delete:
            self.delete(parsed_args)
        else:
            if self.is_allow_create and not parsed_args.entry:
                self.create(parsed_args)
            elif self.is_allow_update and parsed_args.entry:
                self.update(parsed_args)

    def log_create(self, entry):
        """Log creating new model entry."""
        self.app.stdout.write('{}\n'.format(entry.id))
        self.log.info('Create object.')

    def log_update(self, entry):
        """Log updating model entry."""
        self.app.stdout.write('{}\n'.format(entry.id))
        self.log.info('Update object.')

    def log_delete(self, entry):
        """Log deleting model entry."""
        self.app.stdout.write('{}\n'.format(entry.id))
        self.log.info('Delete object.')

    def get_objects(self, ids__names):
        """Get model list.

        Models will match id and label with passed ids__names list.
        """
        ids, names = self.parse_ids_names(ids__names)
        instances = self.storage.filter(
            self.model_class, any,
            **{'id.rcontains': ids, 'label.rcontains': names}
        )
        if not instances:
            raise DoesNotExistException("There aren't any instance.")
        return instances

    # pylint: disable=no-self-use
    def parse_ids_names(self, ids__names):
        """Parse ids__models list."""
        ids = [int(i) for i in ids__names if i.isdigit()]
        return ids, ids__names

    def create_instance(self, args):
        """Create new model entry."""
        instance = self.serialize_args(args)
        with self.storage:
            saved_instance = self.storage.save(instance)
        self.log_create(saved_instance)

    def update_instance(self, args, instance):
        """Update model entry."""
        updated_instance = self.serialize_args(args, instance)
        with self.storage:
            self.storage.save(updated_instance)
            self.log_update(updated_instance)

    def delete_instance(self, instance):
        """Delete model entry."""
        with self.storage:
            self.storage.delete(instance)
            self.log_delete(instance)


# pylint: disable=too-few-public-methods, abstract-method
class ListCommand(Lister):
    """Command for listing storage content."""

    log = logging.getLogger(__name__)

    def __init__(self, app, app_args, cmd_name=None):
        """Create new command instance."""
        super(ListCommand, self).__init__(app, app_args, cmd_name)
        self.config = Config(self.app.NAME)
        self.storage = ApplicationStorage(self.app.NAME)

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(ListCommand, self).get_parser(prog_name)
        parser.add_argument('--log-file', help='Path to log file.')
        return parser
