# -*- coding: utf-8 -*-
"""Module with Snippet commands."""
from ..core.commands import ListCommand, DetailCommand
from ..core.commands.single import RequiredOptions
from ..core.models.terminal import Snippet


class SnippetCommand(DetailCommand):
    """Operate with Group object."""

    model_class = Snippet
    required_options = RequiredOptions(create=('script',))

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-s', '--script', metavar='SCRIPT',
            help='Shell Script for snippet.'
        )
        return parser

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

    model_class = Snippet
