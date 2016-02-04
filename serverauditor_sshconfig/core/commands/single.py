# -*- coding: utf-8 -*-
"""Module with base commands per entries."""
from ..exceptions import ArgumentRequiredException
from ..storage.strategies import (
    RelatedSaveStrategy,
    RelatedGetStrategy,
)
from .mixins import GetRelationMixin, GetObjectsMixin, InstanceOpertionMixin
from .base import AbstractCommand


class DetailCommand(GetRelationMixin, GetObjectsMixin,
                    InstanceOpertionMixin, AbstractCommand):
    """Command for operating with models by id or names."""

    save_strategy = RelatedSaveStrategy
    get_strategy = RelatedGetStrategy

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

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(DetailCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-d', '--delete',
            action='store_true', help='Delete entries.'
        )
        parser.add_argument(
            '-I', '--interactive', action='store_true',
            help='Enter to interactive mode.'
        )
        parser.add_argument(
            '-L', '--label', metavar='NAME',
            help="Entry's label in Serverauditor"
        )
        parser.add_argument(
            'entry', nargs='*', metavar='ID or NAME',
            help='Pass to edit exited entries.'
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
