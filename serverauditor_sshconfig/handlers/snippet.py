# -*- coding: utf-8 -*-
"""Module with Snippet commands."""
from operator import attrgetter
from ..core.commands import ListCommand, DetailCommand
from ..core.exceptions import ArgumentRequiredException
from ..core.models.terminal import Snippet


class SnippetCommand(DetailCommand):
    """Operate with Group object."""

    model_class = Snippet

    def get_parser(self, prog_name):
        """Create command line argument parser.

        Use it to add extra options to argument parser.
        """
        parser = super(SnippetCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-s', '--script', metavar='SCRIPT',
            help='Shell Script for snippet.'
        )
        parser.add_argument(
            'snippet', nargs='?', metavar='SNIPPET_ID or SNIPPET_NAME',
            help='Pass to edit exited snippets.'
        )
        return parser

    def create(self, parsed_args):
        """Handle create new instance command."""
        if not parsed_args.script:
            raise ArgumentRequiredException('Script is required')

        self.create_instance(parsed_args)

    # pylint: disable=no-self-use
    def serialize_args(self, args, instance=None):
        """Convert args to instance."""
        if instance:
            snippet = instance
        else:
            snippet = Snippet()

        snippet.script = args.script
        snippet.label = args.label
        return snippet


class SnippetsCommand(ListCommand):
    """Manage snippet objects."""

    # pylint: disable=unused-argument
    def take_action(self, parsed_args):
        """Process CLI call."""
        groups = self.storage.get_all(Snippet)
        fields = Snippet.allowed_fields()
        getter = attrgetter(*fields)
        return fields, [getter(i) for i in groups]
