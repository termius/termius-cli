# -*- coding: utf-8 -*-
"""Module with base commands per entries."""
from collections import namedtuple
from ..exceptions import ArgumentRequiredException
from ..storage.strategies import (
    RelatedSaveStrategy,
    RelatedGetStrategy,
)
from .mixins import GetRelationMixin, GetObjectsMixin, InstanceOperationMixin
from .base import AbstractCommand


class RequiredOptions(namedtuple('RequiredOptions',
                                 ['create', 'update', 'delete'])):
    """Class for keeping required options."""

    @staticmethod
    def __new__(cls, create=(), update=('entry',), delete=('entry',)):
        """Make field optionals."""
        return super(RequiredOptions, cls).__new__(cls, create, update, delete)


class DetailCommand(GetRelationMixin, GetObjectsMixin,
                    InstanceOperationMixin, AbstractCommand):
    """Command for operating with models by id or names."""

    save_strategy = RelatedSaveStrategy
    get_strategy = RelatedGetStrategy

    required_options = RequiredOptions()

    def create(self, parsed_args):
        """Handle create new instance command."""
        self.validate_args(parsed_args, 'create')
        self.create_instance(parsed_args)

    def update(self, parsed_args):
        """Handle update command.

        Get models from storage, parse args and update models.
        """
        self.validate_args(parsed_args, 'update')
        instances = self.get_objects(parsed_args.entry)
        for i in instances:
            self.update_instance(parsed_args, i)

    def delete(self, parsed_args):
        """Handle delete command.

        Get models from storage, delete models.
        """
        self.validate_args(parsed_args, 'delete')
        instances = self.get_objects(parsed_args.entry)
        for i in instances:
            self.delete_instance(i)

    def get_parser(self, prog_name):
        """Add more arguments to parser."""
        parser = super(DetailCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='delete entries'
        )
        parser.add_argument(
            '-L', '--label', metavar='NAME',
            help="name or rename the entry label NAME"
        )
        parser.add_argument(
            'entry', nargs='*', metavar='ID or NAME',
            help='select the entry with ID or NAME'
        )
        return parser

    def take_action(self, parsed_args):
        """Process CLI call."""
        if parsed_args.delete:
            self.delete(parsed_args)
        elif not parsed_args.entry:
            self.create(parsed_args)
        else:
            self.update(parsed_args)

    def validate_args(self, args, action):
        """Raise ArgumentRequiredException if any required options' missed."""
        arg_list = getattr(self.required_options, action)
        missed_options_list = [
            i for i in arg_list if getattr(args, i) is None
        ]
        if missed_options_list:
            message = self.generate_requirement_message(missed_options_list)
            raise ArgumentRequiredException(message)

    # pylint: disable=no-self-use
    def generate_requirement_message(self, options):
        """Render error message for missed required options."""
        if len(options) == 1:
            return 'Option {} is required!'.format(options[0])
        else:
            return 'Options {} are required!'.format(','.join(options))
