# -*- coding: utf-8 -*-
"""Module with Snippet commands."""
from ..core.commands import ListCommand, DetailCommand
from ..core.commands.single import RequiredOptions
from ..core.models.terminal import Snippet


class SnippetCommand(DetailCommand):
    """work with snippet"""

    model_class = Snippet
    required_options = RequiredOptions(create=('script', 'label'))

    def extend_parser(self, parser):
        """Add more arguments to parser."""
        parser.add_argument(
            '-s', '--script', metavar='SCRIPT',
            help='shell script for snippet'
        )
        return parser


class SnippetsCommand(ListCommand):
    """list all snippets"""

    model_class = Snippet
